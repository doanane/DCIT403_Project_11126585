from src.core.agent import Agent
from src.core.message import Message, Performative
from src.beliefs.drug_belief import ExpiryStatus

# A batch is flagged EXPIRING_SOON when this many steps remain before expiry.
EXPIRING_SOON_THRESHOLD = 3
# A batch receives a WARNING when this many steps remain before expiry.
WARNING_THRESHOLD = 6


class ExpiryMonitorAgent(Agent):
    """
    Proactively scans every drug batch in every ward each simulation step.

    Responsibilities:
    - Detect batches that have already expired and raise an immediate alert.
    - Detect batches that will expire within WARNING_THRESHOLD steps and issue warnings.
    - Enforce FEFO (First Expired, First Out): when a ward holds multiple batches of
      the same drug, log that the soonest-expiring batch must be consumed first.
    - Maintain an expiry_alerts dict (readable by the UI) keyed by batch_id.
    """

    def __init__(self, agent_system, drug_db, log_callback=None):
        super().__init__("ExpiryMonitorAgent", agent_system, log_callback)
        self.drug_db = drug_db
        # batch_id -> alert info dict; accessible by the UI
        self.expiry_alerts = {}
        # Tracks (batch_id, ExpiryStatus) pairs that have already been logged
        # so repeated steps do not flood the log with duplicate lines.
        self._logged_alerts = set()

    # ------------------------------------------------------------------
    # Agent interface
    # ------------------------------------------------------------------

    def handle_message(self, message):
        if message.performative == Performative.EXPIRY_ALERT:
            # Currently no agent sends EXPIRY_ALERT to this agent, but the
            # handler is here for future extension.
            pass

    def proactive_step(self):
        self._plan_scan_expiry()
        self._plan_enforce_fefo()

    # ------------------------------------------------------------------
    # Internal plans
    # ------------------------------------------------------------------

    def _classify_batch(self, batch):
        steps_remaining = batch.expiry_step - self.current_step
        if steps_remaining <= 0:
            return ExpiryStatus.EXPIRED
        if steps_remaining <= EXPIRING_SOON_THRESHOLD:
            return ExpiryStatus.EXPIRING_SOON
        if steps_remaining <= WARNING_THRESHOLD:
            return ExpiryStatus.WARNING
        return ExpiryStatus.OK

    def _plan_scan_expiry(self):
        """Classify every tracked batch and update expiry_alerts."""
        for batch in self.drug_db.get_all_batches():
            status = self._classify_batch(batch)
            drug = self.drug_db.get_drug(batch.drug_id)
            drug_name = drug.name if drug else batch.drug_id
            unit = drug.unit if drug else "units"
            steps_remaining = batch.expiry_step - self.current_step

            # Keep or create the alert record for every non-OK batch.
            if status != ExpiryStatus.OK:
                if batch.batch_id not in self.expiry_alerts:
                    self.expiry_alerts[batch.batch_id] = {
                        "batch_id": batch.batch_id,
                        "drug_id": batch.drug_id,
                        "drug_name": drug_name,
                        "ward_id": batch.ward_id,
                        "quantity": batch.quantity,
                        "expiry_step": batch.expiry_step,
                        "status": status.value,
                        "detected_step": self.current_step,
                    }
                else:
                    self.expiry_alerts[batch.batch_id]["status"] = status.value
            else:
                # If a batch transitions back to OK (should not happen in
                # simulation, but guard anyway), remove the alert.
                self.expiry_alerts.pop(batch.batch_id, None)

            # Log each status level once per batch (not every step).
            alert_key = (batch.batch_id, status)
            if status != ExpiryStatus.OK and alert_key not in self._logged_alerts:
                self._logged_alerts.add(alert_key)
                if status == ExpiryStatus.EXPIRED:
                    self.log(
                        f"EXPIRY ALERT [EXPIRED] Batch {batch.batch_id}: "
                        f"{drug_name} in {batch.ward_id} "
                        f"({batch.quantity} {unit}) expired at step "
                        f"{batch.expiry_step}. Remove from use immediately."
                    )
                    self._send_expiry_alert(batch, status, drug_name, steps_remaining)
                elif status == ExpiryStatus.EXPIRING_SOON:
                    self.log(
                        f"EXPIRY ALERT [EXPIRING SOON] Batch {batch.batch_id}: "
                        f"{drug_name} in {batch.ward_id} "
                        f"({batch.quantity} {unit}) expires in "
                        f"{steps_remaining} step(s) (step {batch.expiry_step}). "
                        f"Use immediately."
                    )
                    self._send_expiry_alert(batch, status, drug_name, steps_remaining)
                elif status == ExpiryStatus.WARNING:
                    self.log(
                        f"EXPIRY WARNING Batch {batch.batch_id}: "
                        f"{drug_name} in {batch.ward_id} "
                        f"({batch.quantity} {unit}) expires in "
                        f"{steps_remaining} step(s) (step {batch.expiry_step})."
                    )

    def _plan_enforce_fefo(self):
        """
        For each drug/ward combination that has more than one batch, log
        FEFO ordering if the earliest-expiring batch is at WARNING level
        or worse.
        """
        batches_by_key = {}
        for batch in self.drug_db.get_all_batches():
            key = (batch.drug_id, batch.ward_id)
            batches_by_key.setdefault(key, []).append(batch)

        for (drug_id, ward_id), batches in batches_by_key.items():
            if len(batches) < 2:
                continue
            sorted_batches = sorted(batches, key=lambda b: b.expiry_step)
            earliest = sorted_batches[0]
            latest = sorted_batches[-1]
            earliest_status = self._classify_batch(earliest)

            if earliest_status in (
                ExpiryStatus.EXPIRED,
                ExpiryStatus.EXPIRING_SOON,
                ExpiryStatus.WARNING,
            ):
                fefo_key = (drug_id, ward_id, earliest_status, self.current_step)
                if fefo_key not in self._logged_alerts:
                    self._logged_alerts.add(fefo_key)
                    drug = self.drug_db.get_drug(drug_id)
                    drug_name = drug.name if drug else drug_id
                    self.log(
                        f"FEFO ORDER: {drug_name} in {ward_id} - "
                        f"use batch {earliest.batch_id} "
                        f"(exp step {earliest.expiry_step}) BEFORE "
                        f"batch {latest.batch_id} "
                        f"(exp step {latest.expiry_step})."
                    )

    def _send_expiry_alert(self, batch, status, drug_name, steps_remaining):
        """Broadcast an EXPIRY_ALERT message via the agent system."""
        msg = Message(
            performative=Performative.EXPIRY_ALERT,
            sender=self.name,
            recipient="ProcurementEscalationAgent",
            content={
                "batch_id": batch.batch_id,
                "drug_id": batch.drug_id,
                "drug_name": drug_name,
                "ward_id": batch.ward_id,
                "quantity": batch.quantity,
                "expiry_step": batch.expiry_step,
                "status": status.value,
                "steps_remaining": steps_remaining,
                "step": self.current_step,
            },
        )
        self.send(msg)

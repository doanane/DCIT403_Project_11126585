from src.core.agent import Agent
from src.core.message import Message, Performative
from src.beliefs.supplier_belief import ProcurementStatus

ESCALATION_TIMEOUT_STEPS = 5


class ProcurementEscalationAgent(Agent):
    def __init__(self, agent_system, drug_db, supplier_db, log_callback=None):
        super().__init__("ProcurementEscalationAgent", agent_system, log_callback)
        self.drug_db = drug_db
        self.supplier_db = supplier_db
        self.pending_procurements = {}
        self.resolved_shortages = {}
        self.expiry_escalations = {}
        self._awaiting_transfer = {}

    def handle_message(self, message):
        if message.performative == Performative.SHORTAGE_CLASSIFIED:
            self._plan_handle_shortage_classified(message.content)
        elif message.performative == Performative.TRANSFER_RESULT:
            self._plan_handle_transfer_result(message.content)
        elif message.performative == Performative.EXPIRY_ALERT:
            self._plan_handle_expiry_alert(message.content)

    def _plan_handle_shortage_classified(self, content):
        shortage_id = content["shortage_id"]
        await_transfer = content.get("await_transfer_result", False)

        if await_transfer:
            self._awaiting_transfer[shortage_id] = content
            self.log(
                f"Shortage {shortage_id} awaiting transfer result before procurement decision"
            )
        else:
            self._initiate_procurement(content)

    def _plan_handle_transfer_result(self, content):
        shortage_id = content["shortage_id"]

        if content["success"]:
            self.log(
                f"Transfer succeeded for shortage {shortage_id} -> marking resolved"
            )
            self.resolved_shortages[shortage_id] = {
                "shortage_id": shortage_id,
                "drug_id": content["drug_id"],
                "drug_name": content["drug_name"],
                "ward_id": content["ward_id"],
                "resolution": "transfer",
                "step": content["step"]
            }
            if shortage_id in self._awaiting_transfer:
                del self._awaiting_transfer[shortage_id]
            return

        self.log(
            f"Transfer failed for shortage {shortage_id} (reason: {content.get('reason', 'unknown')}) "
            f"-> initiating procurement"
        )

        awaiting_content = self._awaiting_transfer.pop(shortage_id, None)
        source_content = awaiting_content if awaiting_content else content
        self._initiate_procurement(source_content)

    def _plan_handle_expiry_alert(self, content):
        """Record and log escalated expiry alerts from ExpiryMonitorAgent."""
        batch_id = content["batch_id"]
        status = content["status"]
        existing = self.expiry_escalations.get(batch_id)

        # Ignore duplicate status updates for the same batch.
        if existing and existing["status"] == status:
            return

        self.expiry_escalations[batch_id] = {
            "batch_id": batch_id,
            "drug_id": content["drug_id"],
            "drug_name": content["drug_name"],
            "ward_id": content["ward_id"],
            "quantity": content["quantity"],
            "expiry_step": content["expiry_step"],
            "status": status,
            "steps_remaining": content["steps_remaining"],
            "step": content["step"],
        }

        self.log(
            f"EXPIRY ESCALATION received: Batch {batch_id} "
            f"({content['drug_name']} in {content['ward_id']}) -> {status}"
        )

    def _initiate_procurement(self, content):
        shortage_id = content["shortage_id"]

        if shortage_id in self.pending_procurements or shortage_id in self.resolved_shortages:
            return

        drug_id = content["drug_id"]
        drug_name = content["drug_name"]
        ward_id = content["ward_id"]
        quantity_needed = content["quantity_needed"]
        category = content["category"].lower()
        step = content["step"]

        drug = self.drug_db.get_drug(drug_id)
        is_controlled = category == "controlled"

        supplier = self.supplier_db.find_supplier(category)
        if supplier is None:
            self.log(f"No supplier found for category {category} for shortage {shortage_id}")
            return

        record = self.supplier_db.create_procurement(
            drug_id=drug_id,
            drug_name=drug_name,
            ward_id=ward_id,
            quantity_requested=quantity_needed,
            supplier_id=supplier.supplier_id,
            supplier_name=supplier.name,
            status=ProcurementStatus.REQUESTED,
            requested_step=step,
            is_controlled=is_controlled
        )

        self.pending_procurements[shortage_id] = {
            "shortage_id": shortage_id,
            "record_id": record.record_id,
            "drug_id": drug_id,
            "drug_name": drug_name,
            "ward_id": ward_id,
            "dispatch_step": self.current_step,
            "status": ProcurementStatus.REQUESTED,
            "procurement_record": record
        }

        self.log(
            f"Procurement initiated: {record.record_id} for {drug_name} in {ward_id} "
            f"via {supplier.name} (qty={quantity_needed}, controlled={is_controlled})"
        )

    def proactive_step(self):
        self._plan_check_and_escalate()

    def _plan_check_and_escalate(self):
        for shortage_id, proc in list(self.pending_procurements.items()):
            if proc["status"] == ProcurementStatus.REQUESTED:
                steps_elapsed = self.current_step - proc["dispatch_step"]
                if steps_elapsed >= ESCALATION_TIMEOUT_STEPS:
                    proc["status"] = ProcurementStatus.ESCALATED
                    record = proc["procurement_record"]
                    record.status = ProcurementStatus.ESCALATED
                    record.escalated_step = self.current_step
                    self.log(
                        f"ESCALATION: Procurement {record.record_id} for {proc['drug_name']} "
                        f"in {proc['ward_id']} escalated after {steps_elapsed} steps"
                    )

    def simulate_supplier_confirmation(self, shortage_id, step):
        if shortage_id not in self.pending_procurements:
            return
        proc = self.pending_procurements[shortage_id]
        if proc["status"] == ProcurementStatus.REQUESTED:
            proc["status"] = ProcurementStatus.CONFIRMED
            record = proc["procurement_record"]
            record.status = ProcurementStatus.CONFIRMED
            record.confirmed_step = step
            self.log(
                f"Supplier confirmation received for {record.record_id} "
                f"({proc['drug_name']} in {proc['ward_id']}) at step {step}"
            )

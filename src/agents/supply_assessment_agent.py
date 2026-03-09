from src.core.agent import Agent
from src.core.message import Message, Performative
from src.beliefs.drug_belief import SeverityLevel


class SupplyAssessmentAgent(Agent):
    def __init__(self, agent_system, drug_db, log_callback=None):
        super().__init__("SupplyAssessmentAgent", agent_system, log_callback)
        self.drug_db = drug_db
        self.active_shortages = {}

    def handle_message(self, message):
        if message.performative == Performative.STOCK_ALERT:
            self._plan_classify_shortage(message.content)

    def _plan_classify_shortage(self, content):
        drug_id = content["drug_id"]
        ward_id = content["ward_id"]
        shortage_id = f"{drug_id}_{ward_id}"

        if shortage_id in self.active_shortages:
            return

        drug = self.drug_db.get_drug(drug_id)
        severity_str = content["severity"]
        severity = SeverityLevel(severity_str)
        category = drug.category.value

        shortage_info = {
            "shortage_id": shortage_id,
            "drug_id": drug_id,
            "drug_name": drug.name,
            "ward_id": ward_id,
            "severity": severity_str,
            "category": category,
            "current_stock": content["current_stock"],
            "reorder_threshold": content["reorder_threshold"],
            "quantity_needed": content["quantity_needed"],
            "step_detected": content["step"],
            "status": "ACTIVE"
        }
        self.active_shortages[shortage_id] = shortage_info

        self.log(
            f"Shortage classified: {drug.name} in {ward_id} | "
            f"severity={severity_str} | category={category} | "
            f"need={content['quantity_needed']} {drug.unit}"
        )

        classified_content = {
            "shortage_id": shortage_id,
            "drug_id": drug_id,
            "drug_name": drug.name,
            "ward_id": ward_id,
            "severity": severity_str,
            "category": category,
            "current_stock": content["current_stock"],
            "reorder_threshold": content["reorder_threshold"],
            "quantity_needed": content["quantity_needed"],
            "step": content["step"]
        }

        if severity == SeverityLevel.CRITICAL:
            self.log(f"Plan: CRITICAL -> sending to TransferCoordinationAgent AND ProcurementEscalationAgent")
            transfer_msg = Message(
                performative=Performative.SHORTAGE_CLASSIFIED,
                sender=self.name,
                recipient="TransferCoordinationAgent",
                content=dict(classified_content)
            )
            self.send(transfer_msg)

            proc_content = dict(classified_content)
            proc_content["await_transfer_result"] = True
            proc_msg = Message(
                performative=Performative.SHORTAGE_CLASSIFIED,
                sender=self.name,
                recipient="ProcurementEscalationAgent",
                content=proc_content
            )
            self.send(proc_msg)

        elif severity == SeverityLevel.HIGH:
            self.log(f"Plan: HIGH -> sending to TransferCoordinationAgent only (transfer-first)")
            transfer_msg = Message(
                performative=Performative.SHORTAGE_CLASSIFIED,
                sender=self.name,
                recipient="TransferCoordinationAgent",
                content=dict(classified_content)
            )
            self.send(transfer_msg)

        elif severity == SeverityLevel.MEDIUM:
            self.log(f"Plan: MEDIUM -> sending to ProcurementEscalationAgent only (procurement watch)")
            proc_msg = Message(
                performative=Performative.SHORTAGE_CLASSIFIED,
                sender=self.name,
                recipient="ProcurementEscalationAgent",
                content=dict(classified_content)
            )
            self.send(proc_msg)

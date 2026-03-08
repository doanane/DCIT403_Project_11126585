from src.core.agent import Agent
from src.core.message import Message, Performative
from src.beliefs.drug_belief import DrugCategory
from src.beliefs.ward_belief import TransferStatus


class TransferCoordinationAgent(Agent):
    def __init__(self, agent_system, drug_db, ward_db, log_callback=None):
        super().__init__("TransferCoordinationAgent", agent_system, log_callback)
        self.drug_db = drug_db
        self.ward_db = ward_db

    def handle_message(self, message):
        if message.performative == Performative.SHORTAGE_CLASSIFIED:
            self._plan_coordinate_transfer(message.content)

    def _plan_coordinate_transfer(self, content):
        shortage_id = content["shortage_id"]
        drug_id = content["drug_id"]
        drug_name = content["drug_name"]
        ward_id = content["ward_id"]
        quantity_needed = content["quantity_needed"]
        category = content["category"]
        step = content["step"]

        drug = self.drug_db.get_drug(drug_id)

        if drug.category == DrugCategory.CONTROLLED:
            self.log(
                f"Transfer request for {drug_name} in {ward_id} DENIED: "
                f"controlled substance policy prohibits internal transfer"
            )
            transfer_record = self.ward_db.create_transfer(
                drug_id=drug_id,
                drug_name=drug_name,
                from_ward_id="N/A",
                to_ward_id=ward_id,
                quantity=0,
                status=TransferStatus.FAILED,
                initiated_step=step
            )
            transfer_record.completed_step = step
            result_msg = Message(
                performative=Performative.TRANSFER_RESULT,
                sender=self.name,
                recipient="ProcurementEscalationAgent",
                content={
                    "shortage_id": shortage_id,
                    "drug_id": drug_id,
                    "drug_name": drug_name,
                    "ward_id": ward_id,
                    "success": False,
                    "reason": "controlled_substance_policy",
                    "severity": content["severity"],
                    "category": category,
                    "quantity_needed": quantity_needed,
                    "step": step
                }
            )
            self.send(result_msg)
            return

        all_wards = self.ward_db.get_all_wards()
        donor_ward = None
        donor_stock_record = None

        for ward in all_wards:
            if ward.ward_id == ward_id:
                continue
            stock = self.drug_db.get_stock(drug_id, ward.ward_id)
            if stock is None:
                continue
            reorder_threshold = stock.reorder_threshold
            if reorder_threshold == 0:
                continue
            surplus_ratio = stock.current_stock / reorder_threshold
            if surplus_ratio > 0.5 and stock.current_stock > quantity_needed * 0.5:
                donor_ward = ward
                donor_stock_record = stock
                break

        if donor_ward is None:
            self.log(f"No suitable donor found for {drug_name} to {ward_id}")
            transfer_record = self.ward_db.create_transfer(
                drug_id=drug_id,
                drug_name=drug_name,
                from_ward_id="N/A",
                to_ward_id=ward_id,
                quantity=0,
                status=TransferStatus.FAILED,
                initiated_step=step
            )
            transfer_record.completed_step = step
            result_msg = Message(
                performative=Performative.TRANSFER_RESULT,
                sender=self.name,
                recipient="ProcurementEscalationAgent",
                content={
                    "shortage_id": shortage_id,
                    "drug_id": drug_id,
                    "drug_name": drug_name,
                    "ward_id": ward_id,
                    "success": False,
                    "reason": "no_donor_available",
                    "severity": content["severity"],
                    "category": category,
                    "quantity_needed": quantity_needed,
                    "step": step
                }
            )
            self.send(result_msg)
            return

        transfer_qty = min(quantity_needed, int(donor_stock_record.current_stock * 0.5))

        recipient_stock = self.drug_db.get_stock(drug_id, ward_id)
        new_donor_stock = donor_stock_record.current_stock - transfer_qty
        new_recipient_stock = (recipient_stock.current_stock if recipient_stock else 0) + transfer_qty

        self.drug_db.set_stock(drug_id, donor_ward.ward_id, new_donor_stock, step)
        self.drug_db.set_stock(drug_id, ward_id, new_recipient_stock, step)

        transfer_record = self.ward_db.create_transfer(
            drug_id=drug_id,
            drug_name=drug_name,
            from_ward_id=donor_ward.ward_id,
            to_ward_id=ward_id,
            quantity=transfer_qty,
            status=TransferStatus.COMPLETED,
            initiated_step=step
        )
        transfer_record.completed_step = step

        self.log(
            f"Transfer SUCCESS: {transfer_qty} {drug.unit} of {drug_name} "
            f"from {donor_ward.ward_id} to {ward_id} (record {transfer_record.transfer_id})"
        )

        result_msg = Message(
            performative=Performative.TRANSFER_RESULT,
            sender=self.name,
            recipient="ProcurementEscalationAgent",
            content={
                "shortage_id": shortage_id,
                "drug_id": drug_id,
                "drug_name": drug_name,
                "ward_id": ward_id,
                "success": True,
                "transfer_id": transfer_record.transfer_id,
                "transfer_qty": transfer_qty,
                "from_ward": donor_ward.ward_id,
                "severity": content["severity"],
                "category": category,
                "quantity_needed": quantity_needed,
                "step": step
            }
        )
        self.send(result_msg)

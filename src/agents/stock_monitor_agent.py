from src.core.agent import Agent
from src.core.message import Message, Performative
from src.beliefs.drug_belief import SeverityLevel


class StockMonitorAgent(Agent):
    def __init__(self, agent_system, drug_db, log_callback=None):
        super().__init__("StockMonitorAgent", agent_system, log_callback)
        self.drug_db = drug_db
        self.alerted_stocks = set()

    def handle_message(self, message):
        if message.performative == Performative.STOCK_READING:
            self._plan_process_reading(message.content)

    def _plan_process_reading(self, content):
        drug_id = content["drug_id"]
        ward_id = content["ward_id"]
        quantity = content["quantity"]
        step = content["step"]

        self.drug_db.set_stock(drug_id, ward_id, quantity, step)
        record = self.drug_db.get_stock(drug_id, ward_id)
        drug = self.drug_db.get_drug(drug_id)
        severity = record.severity()

        level_pct = (quantity / record.reorder_threshold * 100) if record.reorder_threshold > 0 else 0
        self.log(
            f"Stock reading: {drug.name} in {ward_id} = {quantity} {drug.unit} "
            f"({level_pct:.1f}% of threshold) -> {severity.value}"
        )

        alert_key = (drug_id, ward_id)
        if severity in (SeverityLevel.CRITICAL, SeverityLevel.HIGH, SeverityLevel.MEDIUM):
            if alert_key not in self.alerted_stocks:
                self.alerted_stocks.add(alert_key)
                quantity_needed = record.reorder_threshold - quantity
                msg = Message(
                    performative=Performative.STOCK_ALERT,
                    sender=self.name,
                    recipient="SupplyAssessmentAgent",
                    content={
                        "drug_id": drug_id,
                        "ward_id": ward_id,
                        "current_stock": quantity,
                        "reorder_threshold": record.reorder_threshold,
                        "severity": severity.value,
                        "quantity_needed": quantity_needed,
                        "step": step
                    }
                )
                self.send(msg)
                self.log(
                    f"STOCK_ALERT sent for {drug.name} in {ward_id} "
                    f"(severity={severity.value}, need={quantity_needed} {drug.unit})"
                )

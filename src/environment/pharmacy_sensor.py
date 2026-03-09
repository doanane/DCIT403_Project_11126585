from src.core.message import Message, Performative


class PharmacySensor:
    def __init__(self, agent_system):
        self.agent_system = agent_system
        self._schedule = []

    def schedule_reading(self, step, drug_id, ward_id, quantity):
        self._schedule.append((step, drug_id, ward_id, quantity))

    def emit(self, current_step):
        for entry in self._schedule:
            step, drug_id, ward_id, quantity = entry
            if step == current_step:
                msg = Message(
                    performative=Performative.STOCK_READING,
                    sender="PharmacySensor",
                    recipient="StockMonitorAgent",
                    content={
                        "drug_id": drug_id,
                        "ward_id": ward_id,
                        "quantity": quantity,
                        "step": current_step
                    }
                )
                self.agent_system.deliver(msg)

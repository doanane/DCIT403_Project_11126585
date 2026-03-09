from src.core.agent_system import AgentSystem
from src.beliefs.drug_belief import DrugDatabase, Drug, DrugCategory
from src.beliefs.ward_belief import WardDatabase, Ward
from src.beliefs.supplier_belief import SupplierDatabase, Supplier
from src.environment.pharmacy_sensor import PharmacySensor
from src.agents.stock_monitor_agent import StockMonitorAgent
from src.agents.supply_assessment_agent import SupplyAssessmentAgent
from src.agents.transfer_coordination_agent import TransferCoordinationAgent
from src.agents.procurement_escalation_agent import ProcurementEscalationAgent

TOTAL_STEPS = 20


class MedStockSimulator:
    def __init__(self, log_callback=None):
        self.log_callback = log_callback
        self.total_steps = TOTAL_STEPS
        self._initialize()

    def _initialize(self):
        self.current_step = 0
        self.agent_system = AgentSystem()

        self.drug_db = DrugDatabase()
        self.ward_db = WardDatabase()
        self.supplier_db = SupplierDatabase()

        self._setup_drugs()
        self._setup_wards()
        self._setup_suppliers()
        self._setup_initial_stock()
        self._setup_agents()
        self._setup_sensor()
        self._schedule_sensor_events()

    def _setup_drugs(self):
        self.drug_db.add_drug(Drug("insulin", "Insulin", DrugCategory.ESSENTIAL, "units", 100))
        self.drug_db.add_drug(Drug("morphine", "Morphine", DrugCategory.CONTROLLED, "mg", 50))
        self.drug_db.add_drug(Drug("amoxicillin", "Amoxicillin", DrugCategory.ESSENTIAL, "tablets", 200))
        self.drug_db.add_drug(Drug("paracetamol", "Paracetamol", DrugCategory.STANDARD, "tablets", 500))
        self.drug_db.add_drug(Drug("iv_fluids", "IV Fluids", DrugCategory.ESSENTIAL, "bags", 300))

    def _setup_wards(self):
        self.ward_db.add_ward(Ward("ICU", "Intensive Care Unit", 5))
        self.ward_db.add_ward(Ward("EMERGENCY", "Emergency Department", 4))
        self.ward_db.add_ward(Ward("SURGICAL", "Surgical Ward", 3))
        self.ward_db.add_ward(Ward("MATERNITY", "Maternity Ward", 2))
        self.ward_db.add_ward(Ward("GENERAL", "General Ward", 1))

    def _setup_suppliers(self):
        self.supplier_db.add_supplier(Supplier("MEDPHARM", "MedPharm Ghana Ltd", ["essential"], 3))
        self.supplier_db.add_supplier(Supplier("PHARMACTL", "PharmaControl Ltd", ["controlled"], 5))
        self.supplier_db.add_supplier(Supplier("BASICMEDS", "BasicMeds Supplies", ["standard"], 2))

    def _setup_initial_stock(self):
        stocks = {
            "insulin":     {"ICU": 8,   "EMERGENCY": 120, "SURGICAL": 85,  "MATERNITY": 90,  "GENERAL": 180},
            "morphine":    {"ICU": 45,  "EMERGENCY": 30,  "SURGICAL": 7,   "MATERNITY": 20,  "GENERAL": 15},
            "amoxicillin": {"ICU": 150, "EMERGENCY": 180, "SURGICAL": 40,  "MATERNITY": 160, "GENERAL": 400},
            "paracetamol": {"ICU": 400, "EMERGENCY": 350, "SURGICAL": 300, "MATERNITY": 450, "GENERAL": 160},
            "iv_fluids":   {"ICU": 200, "EMERGENCY": 60,  "SURGICAL": 190, "MATERNITY": 220, "GENERAL": 350},
        }
        for drug_id, ward_stocks in stocks.items():
            for ward_id, qty in ward_stocks.items():
                self.drug_db.set_stock(drug_id, ward_id, qty, 0)

    def _setup_agents(self):
        self.stock_monitor = StockMonitorAgent(
            self.agent_system, self.drug_db, self.log_callback
        )
        self.supply_assessment = SupplyAssessmentAgent(
            self.agent_system, self.drug_db, self.log_callback
        )
        self.transfer_coord = TransferCoordinationAgent(
            self.agent_system, self.drug_db, self.ward_db, self.log_callback
        )
        self.procurement_escalation = ProcurementEscalationAgent(
            self.agent_system, self.drug_db, self.supplier_db, self.log_callback
        )

        self.agent_system.register(self.stock_monitor)
        self.agent_system.register(self.supply_assessment)
        self.agent_system.register(self.transfer_coord)
        self.agent_system.register(self.procurement_escalation)

    def _setup_sensor(self):
        self.sensor = PharmacySensor(self.agent_system)

    def _schedule_sensor_events(self):
        self.sensor.schedule_reading(1, "insulin", "ICU", 8)
        self.sensor.schedule_reading(3, "morphine", "SURGICAL", 7)
        self.sensor.schedule_reading(8, "amoxicillin", "SURGICAL", 40)
        self.sensor.schedule_reading(10, "paracetamol", "GENERAL", 160)

    def step(self):
        if self.finished:
            return
        self.current_step += 1

        if self.log_callback:
            self.log_callback(f"--- STEP {self.current_step} ---")

        self.sensor.emit(self.current_step)

        self.stock_monitor.run_cycle(self.current_step)
        self.supply_assessment.run_cycle(self.current_step)
        self.transfer_coord.run_cycle(self.current_step)
        self.procurement_escalation.run_cycle(self.current_step)

        if self.current_step == 14:
            self.procurement_escalation.simulate_supplier_confirmation(
                "paracetamol_GENERAL", 14
            )

    def get_stock_summary(self):
        return self.drug_db.get_all_stocks()

    def get_transfers(self):
        return self.ward_db.get_all_transfers()

    def get_procurements(self):
        return self.supplier_db.get_all_procurements()

    def reset(self):
        self._initialize()

    @property
    def finished(self):
        return self.current_step >= self.total_steps

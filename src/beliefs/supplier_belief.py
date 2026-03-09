from dataclasses import dataclass, field
from enum import Enum
from typing import List


class ProcurementStatus(Enum):
    REQUESTED = "REQUESTED"
    CONFIRMED = "CONFIRMED"
    ESCALATED = "ESCALATED"


@dataclass
class Supplier:
    supplier_id: str
    name: str
    drug_categories: List[str]
    lead_time_steps: int


@dataclass
class ProcurementRecord:
    record_id: str
    drug_id: str
    drug_name: str
    ward_id: str
    quantity_requested: float
    supplier_id: str
    supplier_name: str
    status: ProcurementStatus
    requested_step: int
    confirmed_step: int = -1
    escalated_step: int = -1
    is_controlled: bool = False


class SupplierDatabase:
    def __init__(self):
        self._suppliers = {}
        self._procurements = []
        self._procurement_counter = 0

    def add_supplier(self, supplier: Supplier):
        self._suppliers[supplier.supplier_id] = supplier

    def find_supplier(self, drug_category: str):
        for supplier in self._suppliers.values():
            if drug_category in supplier.drug_categories:
                return supplier
        return None

    def create_procurement(self, drug_id, drug_name, ward_id, quantity_requested,
                           supplier_id, supplier_name, status, requested_step,
                           is_controlled=False):
        self._procurement_counter += 1
        record_id = f"PR-{self._procurement_counter:03d}"
        record = ProcurementRecord(
            record_id=record_id,
            drug_id=drug_id,
            drug_name=drug_name,
            ward_id=ward_id,
            quantity_requested=quantity_requested,
            supplier_id=supplier_id,
            supplier_name=supplier_name,
            status=status,
            requested_step=requested_step,
            is_controlled=is_controlled
        )
        self._procurements.append(record)
        return record

    def get_all_procurements(self):
        return list(self._procurements)

    def get_all_suppliers(self):
        return list(self._suppliers.values())

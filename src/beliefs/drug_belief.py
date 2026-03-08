from dataclasses import dataclass
from enum import Enum


class DrugCategory(Enum):
    CONTROLLED = "CONTROLLED"
    ESSENTIAL = "ESSENTIAL"
    STANDARD = "STANDARD"


class SeverityLevel(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    OK = "OK"


@dataclass
class Drug:
    drug_id: str
    name: str
    category: DrugCategory
    unit: str
    reorder_threshold: int


@dataclass
class StockRecord:
    drug_id: str
    ward_id: str
    current_stock: float
    reorder_threshold: float
    last_updated_step: int

    def severity(self):
        if self.reorder_threshold == 0:
            return SeverityLevel.OK
        ratio = self.current_stock / self.reorder_threshold
        if ratio < 0.10:
            return SeverityLevel.CRITICAL
        if ratio < 0.30:
            return SeverityLevel.HIGH
        if ratio < 0.50:
            return SeverityLevel.MEDIUM
        if ratio < 0.75:
            return SeverityLevel.LOW
        return SeverityLevel.OK


class DrugDatabase:
    def __init__(self):
        self._drugs = {}
        self._stocks = {}

    def add_drug(self, drug: Drug):
        self._drugs[drug.drug_id] = drug

    def get_drug(self, drug_id: str):
        return self._drugs.get(drug_id)

    def set_stock(self, drug_id: str, ward_id: str, quantity: float, step: int):
        key = (drug_id, ward_id)
        drug = self._drugs.get(drug_id)
        threshold = drug.reorder_threshold if drug else 0
        self._stocks[key] = StockRecord(
            drug_id=drug_id,
            ward_id=ward_id,
            current_stock=quantity,
            reorder_threshold=threshold,
            last_updated_step=step
        )

    def get_stock(self, drug_id: str, ward_id: str):
        return self._stocks.get((drug_id, ward_id))

    def get_all_stocks(self):
        return list(self._stocks.values())

    def get_all_drugs(self):
        return list(self._drugs.values())

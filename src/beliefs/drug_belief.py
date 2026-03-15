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


class ExpiryStatus(Enum):
    EXPIRED = "EXPIRED"
    EXPIRING_SOON = "EXPIRING_SOON"
    WARNING = "WARNING"
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


@dataclass
class ExpiryBatch:
    """A batch of a drug in a ward with a tracked expiry simulation-step."""
    batch_id: str
    drug_id: str
    ward_id: str
    quantity: float
    expiry_step: int


class DrugDatabase:
    def __init__(self):
        self._drugs = {}
        self._stocks = {}
        self._batches = {}
        self._batch_counter = 0

    def add_drug(self, drug: Drug):
        self._drugs[drug.drug_id] = drug

    def get_drug(self, drug_id: str):
        return self._drugs.get(drug_id)

    def set_stock(self, drug_id: str, ward_id: str, quantity: float, step: int):
        existing = self._stocks.get((drug_id, ward_id))
        if existing:
            delta = quantity - existing.current_stock
            if delta < 0:
                self._consume_batches_fefo(drug_id, ward_id, abs(delta))
            elif delta > 0:
                self._register_restock_batch(drug_id, ward_id, delta, step)

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

    def create_batch(self, drug_id: str, ward_id: str, quantity: float, expiry_step: int) -> ExpiryBatch:
        self._batch_counter += 1
        batch_id = f"BCH-{self._batch_counter:03d}"
        batch = ExpiryBatch(
            batch_id=batch_id,
            drug_id=drug_id,
            ward_id=ward_id,
            quantity=quantity,
            expiry_step=expiry_step
        )
        self._batches[batch_id] = batch
        return batch

    def get_batches_for_drug_ward(self, drug_id: str, ward_id: str):
        return [b for b in self._batches.values()
                if b.drug_id == drug_id and b.ward_id == ward_id]

    def get_all_batches(self):
        return list(self._batches.values())

    def _consume_batches_fefo(self, drug_id: str, ward_id: str, quantity_to_consume: float):
        """Consume stock from earliest-expiring batches first (FEFO)."""
        if quantity_to_consume <= 0:
            return

        candidates = [
            b for b in self._batches.values()
            if b.drug_id == drug_id and b.ward_id == ward_id
        ]
        candidates.sort(key=lambda b: b.expiry_step)

        remaining = quantity_to_consume
        for batch in candidates:
            if remaining <= 0:
                break
            consume = min(batch.quantity, remaining)
            batch.quantity -= consume
            remaining -= consume

        empty_batch_ids = [
            b.batch_id for b in candidates if b.quantity <= 0
        ]
        for batch_id in empty_batch_ids:
            del self._batches[batch_id]

    def _register_restock_batch(self, drug_id: str, ward_id: str, quantity_added: float, step: int):
        """Register newly added stock as a long-dated replenishment batch."""
        if quantity_added <= 0:
            return
        self.create_batch(drug_id, ward_id, quantity_added, step + 24)

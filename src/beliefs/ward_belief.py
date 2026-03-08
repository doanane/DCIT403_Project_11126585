from dataclasses import dataclass, field
from enum import Enum


class TransferStatus(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class Ward:
    ward_id: str
    name: str
    priority: int


@dataclass
class TransferRecord:
    transfer_id: str
    drug_id: str
    drug_name: str
    from_ward_id: str
    to_ward_id: str
    quantity: float
    status: TransferStatus
    initiated_step: int
    completed_step: int = -1


class WardDatabase:
    def __init__(self):
        self._wards = {}
        self._transfers = []
        self._transfer_counter = 0

    def add_ward(self, ward: Ward):
        self._wards[ward.ward_id] = ward

    def get_ward(self, ward_id: str):
        return self._wards.get(ward_id)

    def get_all_wards(self):
        return list(self._wards.values())

    def create_transfer(self, drug_id, drug_name, from_ward_id, to_ward_id, quantity, status, initiated_step):
        self._transfer_counter += 1
        transfer_id = f"TR-{self._transfer_counter:03d}"
        record = TransferRecord(
            transfer_id=transfer_id,
            drug_id=drug_id,
            drug_name=drug_name,
            from_ward_id=from_ward_id,
            to_ward_id=to_ward_id,
            quantity=quantity,
            status=status,
            initiated_step=initiated_step
        )
        self._transfers.append(record)
        return record

    def get_all_transfers(self):
        return list(self._transfers)

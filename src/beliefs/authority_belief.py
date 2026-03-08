import time
from dataclasses import dataclass, field
from typing import Optional, Dict, List


@dataclass
class Authority:
    authority_id: str
    name: str
    jurisdiction: str
    handles_hazardous: bool
    handles_non_hazardous: bool
    response_time_minutes: int
    contact: str

    def __repr__(self):
        return f"Authority({self.authority_id}: {self.name})"


@dataclass
class DispatchRecord:
    incident_id: str
    authority_id: str
    authority_name: str
    dispatched_at: float = field(default_factory=time.time)
    responded_at: Optional[float] = None
    response_status: str = "pending"
    notes: str = ""

    def is_overdue(self, timeout_seconds: int = 30) -> bool:
        if self.response_status == "pending":
            return (time.time() - self.dispatched_at) > timeout_seconds
        return False


class AuthorityDatabase:
    AUTHORITIES: Dict[str, Authority] = {
        "EPA": Authority(
            "EPA",
            "Ghana Environmental Protection Agency",
            "national",
            handles_hazardous=True,
            handles_non_hazardous=True,
            response_time_minutes=45,
            contact="epa-emergency@epa.gov.gh",
        ),
        "HAZMAT": Authority(
            "HAZMAT",
            "National Hazardous Materials Response Unit",
            "national",
            handles_hazardous=True,
            handles_non_hazardous=False,
            response_time_minutes=30,
            contact="hazmat-response@ndpc.gov.gh",
        ),
        "LOCAL_ENV": Authority(
            "LOCAL_ENV",
            "Accra Metropolitan Environmental Officer",
            "local",
            handles_hazardous=False,
            handles_non_hazardous=True,
            response_time_minutes=90,
            contact="env-officer@ama.gov.gh",
        ),
        "REGIONAL": Authority(
            "REGIONAL",
            "Greater Accra Regional Enforcement Unit",
            "regional",
            handles_hazardous=True,
            handles_non_hazardous=True,
            response_time_minutes=60,
            contact="regional-unit@gar.gov.gh",
        ),
    }

    def __init__(self):
        self._dispatch_records: Dict[str, List[DispatchRecord]] = {}

    def get_authority(self, authority_id: str) -> Optional[Authority]:
        return self.AUTHORITIES.get(authority_id)

    def select_authority(self, waste_type: str, severity: str) -> List[str]:
        if waste_type == "hazardous" and severity == "critical":
            return ["EPA", "HAZMAT"]
        if waste_type == "hazardous":
            return ["EPA"]
        if waste_type == "non_hazardous" and severity == "high":
            return ["EPA"]
        if waste_type == "non_hazardous":
            return ["LOCAL_ENV"]
        return ["EPA"]

    def record_dispatch(self, record: DispatchRecord):
        if record.incident_id not in self._dispatch_records:
            self._dispatch_records[record.incident_id] = []
        self._dispatch_records[record.incident_id].append(record)

    def get_dispatch_records(self, incident_id: str) -> List[DispatchRecord]:
        return self._dispatch_records.get(incident_id, [])

    def mark_responded(self, incident_id: str, authority_id: str):
        records = self._dispatch_records.get(incident_id, [])
        for rec in records:
            if rec.authority_id == authority_id:
                rec.responded_at = time.time()
                rec.response_status = "responded"

import time
import uuid
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SensorAlert:
    alert_id: str
    sensor_id: str
    sensor_type: str
    location_key: str
    location_description: str
    reading_value: float
    unit: str
    threshold: float
    timestamp: float = field(default_factory=time.time)

    def exceeds_threshold(self) -> bool:
        return self.reading_value > self.threshold


@dataclass
class CitizenReport:
    report_id: str
    location_key: str
    location_description: str
    description: str
    photo_available: bool
    timestamp: float = field(default_factory=time.time)
    credibility_score: float = 0.6


@dataclass
class Incident:
    incident_id: str
    location_key: str
    location_description: str
    detected_at: float = field(default_factory=time.time)
    sensor_alerts: List[SensorAlert] = field(default_factory=list)
    citizen_reports: List[CitizenReport] = field(default_factory=list)
    waste_type: Optional[str] = None
    severity: Optional[str] = None
    status: str = "detected"
    assigned_authority: Optional[str] = None
    dispatch_time: Optional[float] = None
    evidence_package_id: Optional[str] = None
    escalation_count: int = 0

    def confidence_level(self) -> float:
        sensor_score = min(len(self.sensor_alerts) * 0.3, 0.6)
        report_score = min(len(self.citizen_reports) * 0.2, 0.4)
        return round(sensor_score + report_score, 2)

    def sensor_types_present(self) -> list:
        return list({a.sensor_type for a in self.sensor_alerts})

    def max_reading(self, sensor_type: str) -> Optional[float]:
        readings = [
            a.reading_value
            for a in self.sensor_alerts
            if a.sensor_type == sensor_type
        ]
        return max(readings) if readings else None


class IncidentDatabase:
    def __init__(self):
        self._incidents = {}

    def add_incident(self, incident: Incident):
        self._incidents[incident.incident_id] = incident

    def get(self, incident_id: str) -> Optional[Incident]:
        return self._incidents.get(incident_id)

    def get_by_location(self, location_key: str) -> Optional[Incident]:
        for inc in self._incidents.values():
            if inc.location_key == location_key and inc.status not in ("resolved", "escalated"):
                return inc
        return None

    def update_status(self, incident_id: str, status: str):
        if incident_id in self._incidents:
            self._incidents[incident_id].status = status

    def all_incidents(self) -> list:
        return list(self._incidents.values())

    def pending_dispatch(self) -> list:
        return [
            i for i in self._incidents.values()
            if i.status in ("classified", "evidence_collected")
        ]

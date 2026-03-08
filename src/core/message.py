import time
import uuid
from enum import Enum
from dataclasses import dataclass, field
from typing import Any


class Performative(Enum):
    SENSOR_ALERT = "SENSOR_ALERT"
    CITIZEN_REPORT = "CITIZEN_REPORT"
    INCIDENT_DETECTED = "INCIDENT_DETECTED"
    INCIDENT_UPDATE = "INCIDENT_UPDATE"
    INCIDENT_CLASSIFIED = "INCIDENT_CLASSIFIED"
    DISPATCH_REQUEST = "DISPATCH_REQUEST"
    EVIDENCE_PACKAGE = "EVIDENCE_PACKAGE"
    RESPONSE_UPDATE = "RESPONSE_UPDATE"
    ESCALATION_ALERT = "ESCALATION_ALERT"
    INFORM = "INFORM"
    REQUEST = "REQUEST"


@dataclass
class Message:
    sender: str
    receiver: str
    performative: Performative
    content: dict
    timestamp: float = field(default_factory=time.time)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8].upper())

    def __repr__(self):
        return (
            f"Message(id={self.message_id}, from={self.sender}, "
            f"to={self.receiver}, type={self.performative.value})"
        )

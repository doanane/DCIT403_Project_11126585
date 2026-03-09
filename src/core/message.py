from dataclasses import dataclass, field
from enum import Enum


class Performative(Enum):
    STOCK_READING = "STOCK_READING"
    STOCK_ALERT = "STOCK_ALERT"
    SHORTAGE_CLASSIFIED = "SHORTAGE_CLASSIFIED"
    TRANSFER_RESULT = "TRANSFER_RESULT"
    PROCUREMENT_REQUEST = "PROCUREMENT_REQUEST"
    ESCALATION_NOTICE = "ESCALATION_NOTICE"
    STATUS_UPDATE = "STATUS_UPDATE"


@dataclass
class Message:
    performative: Performative
    sender: str
    recipient: str
    content: dict = field(default_factory=dict)

import time
from dataclasses import dataclass
from typing import List
from src.core.message import Performative, Message


@dataclass
class ReportEvent:
    step: int
    report_id: str
    location_key: str
    location_description: str
    description: str
    photo_available: bool


REPORT_SCHEDULE = [
    ReportEvent(
        step=3,
        report_id="CR-001",
        location_key="LOC-A",
        location_description="Abandoned Industrial Site - Tema Port Road",
        description=(
            "Trucks with no markings unloading metal drums and barrels near "
            "the old factory wall after midnight. Strong toxic chemical smell and fumes."
        ),
        photo_available=True,
    ),
    ReportEvent(
        step=5,
        report_id="CR-002",
        location_key="LOC-B",
        location_description="Roadside Clearing - Accra-Kumasi Highway Km 12",
        description=(
            "Large pile of construction rubble, broken concrete blocks, and old furniture "
            "dumped by the roadside near the bridge. Has been growing for three days."
        ),
        photo_available=True,
    ),
    ReportEvent(
        step=6,
        report_id="CR-003",
        location_key="LOC-B",
        location_description="Roadside Clearing - Accra-Kumasi Highway Km 12",
        description=(
            "Confirming the previous report. More debris added overnight including "
            "mattresses and garbage bags. Blocking part of the road shoulder."
        ),
        photo_available=False,
    ),
    ReportEvent(
        step=10,
        report_id="CR-004",
        location_key="LOC-C",
        location_description="Riverbank - Densu River South Bank",
        description=(
            "Foul-smelling liquid seeping into the river. Unusual discoloration "
            "of water near the south bank. Fish floating near the bank."
        ),
        photo_available=True,
    ),
]


class ReportGenerator:
    def __init__(self):
        self._schedule = {evt.step: [] for evt in REPORT_SCHEDULE}
        for evt in REPORT_SCHEDULE:
            self._schedule[evt.step].append(evt)

    def get_events_for_step(self, step: int) -> List[Message]:
        events = self._schedule.get(step, [])
        messages = []
        for evt in events:
            print(
                f"  [ReportSystem] INCOMING: Report {evt.report_id} "
                f"at {evt.location_key} - "
                f"\"{evt.description[:70]}...\""
                if len(evt.description) > 70
                else f"  [ReportSystem] INCOMING: Report {evt.report_id} "
                f"at {evt.location_key} - \"{evt.description}\""
            )
            msg = Message(
                sender="CitizenPortal",
                receiver="SurveillanceAgent",
                performative=Performative.CITIZEN_REPORT,
                content={
                    "report_id": evt.report_id,
                    "location_key": evt.location_key,
                    "location_description": evt.location_description,
                    "description": evt.description,
                    "photo_available": evt.photo_available,
                    "timestamp": time.time(),
                },
            )
            messages.append(msg)
        return messages

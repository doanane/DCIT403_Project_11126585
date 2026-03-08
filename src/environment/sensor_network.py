import time
from dataclasses import dataclass
from typing import List, Optional
from src.core.message import Performative, Message


@dataclass
class SensorEvent:
    step: int
    alert_id: str
    sensor_id: str
    sensor_type: str
    location_key: str
    location_description: str
    reading_value: float
    unit: str
    threshold: float


SENSOR_SCHEDULE = [
    SensorEvent(
        step=1,
        alert_id="SA-001",
        sensor_id="CHEM-LOC-A-01",
        sensor_type="chemical",
        location_key="LOC-A",
        location_description="Abandoned Industrial Site - Tema Port Road",
        reading_value=157.4,
        unit="ppm",
        threshold=50.0,
    ),
    SensorEvent(
        step=2,
        alert_id="SA-002",
        sensor_id="TEMP-LOC-A-01",
        sensor_type="temperature",
        location_key="LOC-A",
        location_description="Abandoned Industrial Site - Tema Port Road",
        reading_value=134.0,
        unit="degrees_C",
        threshold=45.0,
    ),
    SensorEvent(
        step=7,
        alert_id="SA-003",
        sensor_id="AIR-LOC-C-01",
        sensor_type="air_quality",
        location_key="LOC-C",
        location_description="Riverbank - Densu River South Bank",
        reading_value=310.0,
        unit="AQI",
        threshold=100.0,
    ),
    SensorEvent(
        step=8,
        alert_id="SA-004",
        sensor_id="AIR-LOC-C-02",
        sensor_type="air_quality",
        location_key="LOC-C",
        location_description="Riverbank - Densu River South Bank",
        reading_value=290.0,
        unit="AQI",
        threshold=100.0,
    ),
]


class SensorNetwork:
    def __init__(self):
        self._schedule = {evt.step: [] for evt in SENSOR_SCHEDULE}
        for evt in SENSOR_SCHEDULE:
            self._schedule[evt.step].append(evt)

    def get_events_for_step(self, step: int) -> List[Message]:
        events = self._schedule.get(step, [])
        messages = []
        for evt in events:
            print(
                f"  [SensorNetwork] TRIGGER: Sensor {evt.sensor_id} "
                f"({evt.sensor_type.upper()}) at {evt.location_key} -> "
                f"{evt.reading_value} {evt.unit} "
                f"(threshold: {evt.threshold} {evt.unit})"
            )
            msg = Message(
                sender="SensorNetwork",
                receiver="SurveillanceAgent",
                performative=Performative.SENSOR_ALERT,
                content={
                    "alert_id": evt.alert_id,
                    "sensor_id": evt.sensor_id,
                    "sensor_type": evt.sensor_type,
                    "location_key": evt.location_key,
                    "location_description": evt.location_description,
                    "reading_value": evt.reading_value,
                    "unit": evt.unit,
                    "threshold": evt.threshold,
                    "timestamp": time.time(),
                },
            )
            messages.append(msg)
        return messages

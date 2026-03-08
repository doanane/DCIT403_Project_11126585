from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Location:
    location_key: str
    description: str
    latitude: float
    longitude: float
    zone_type: str

    def __repr__(self):
        return f"Location({self.location_key}: {self.description})"


@dataclass
class HotspotRecord:
    location_key: str
    incident_count: int = 0
    last_incident_time: Optional[float] = None
    is_known_hotspot: bool = False

    def increment(self, timestamp: float):
        self.incident_count += 1
        self.last_incident_time = timestamp
        if self.incident_count >= 2:
            self.is_known_hotspot = True


class LocationDatabase:
    LOCATIONS = {
        "LOC-A": Location("LOC-A", "Abandoned Industrial Site - Tema Port Road", 5.6425, -0.0115, "industrial"),
        "LOC-B": Location("LOC-B", "Roadside Clearing - Accra-Kumasi Highway Km 12", 5.7421, -0.2310, "rural_road"),
        "LOC-C": Location("LOC-C", "Riverbank - Densu River South Bank", 5.5830, -0.3190, "waterway"),
    }

    def __init__(self):
        self._hotspots = {}

    def get_location(self, location_key: str) -> Optional[Location]:
        return self.LOCATIONS.get(location_key)

    def record_incident(self, location_key: str, timestamp: float):
        if location_key not in self._hotspots:
            self._hotspots[location_key] = HotspotRecord(location_key)
        self._hotspots[location_key].increment(timestamp)

    def is_hotspot(self, location_key: str) -> bool:
        record = self._hotspots.get(location_key)
        return record.is_known_hotspot if record else False

    def get_hotspot_record(self, location_key: str) -> Optional[HotspotRecord]:
        return self._hotspots.get(location_key)

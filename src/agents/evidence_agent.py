import time
import uuid

from src.core.agent import Agent
from src.core.message import Message, Performative


class EvidenceAgent(Agent):
    def __init__(self, name: str, agent_system):
        super().__init__(name, agent_system)
        self.beliefs["evidence_records"] = {}
        self.beliefs["compiled_packages"] = {}

    def select_plan(self, percept):
        if isinstance(percept, Message):
            if percept.performative == Performative.INCIDENT_CLASSIFIED:
                return self._plan_collect_evidence
        return None

    def _plan_collect_evidence(self, message: Message):
        content = message.content
        incident_id = content["incident_id"]
        waste_type = content["waste_type"]
        severity = content["severity"]
        sensor_alerts = content.get("sensor_alerts", [])
        citizen_reports = content.get("citizen_reports", [])
        confidence = content.get("confidence", 0.0)

        evidence_items = self._gather_sensor_evidence(sensor_alerts)
        evidence_items += self._gather_report_evidence(citizen_reports)
        evidence_items += self._gather_metadata_evidence(content)

        self.beliefs["evidence_records"][incident_id] = evidence_items
        print(
            f"    [EvidenceAgent] ACT: Evidence collected for {incident_id}. "
            f"{len(evidence_items)} item(s) gathered."
        )
        for item in evidence_items:
            print(f"      - {item['type']}: {item['description']}")

        package_id = f"EP-{str(uuid.uuid4())[:4].upper()}"
        package = {
            "package_id": package_id,
            "incident_id": incident_id,
            "location_key": content["location_key"],
            "location_description": content["location_description"],
            "waste_type": waste_type,
            "severity": severity,
            "confidence": confidence,
            "evidence_items": evidence_items,
            "compiled_at": time.time(),
            "item_count": len(evidence_items),
            "chain_of_custody": [
                {
                    "custodian": "EvidenceAgent",
                    "action": "compiled",
                    "timestamp": time.time(),
                }
            ],
        }
        self.beliefs["compiled_packages"][incident_id] = package

        print(
            f"    [EvidenceAgent] ACT: Evidence package {package_id} compiled "
            f"for incident {incident_id}."
        )

        self.send("EnforcementAgent", Performative.EVIDENCE_PACKAGE, package)
        print(
            f"    [EvidenceAgent] SEND -> EnforcementAgent: "
            f"EVIDENCE_PACKAGE [{package_id}] for incident {incident_id}"
        )

    def _gather_sensor_evidence(self, sensor_alerts) -> list:
        items = []
        for alert in sensor_alerts:
            items.append(
                {
                    "type": "sensor_reading",
                    "description": (
                        f"{alert['type'].upper()} sensor: "
                        f"{alert['value']} {alert['unit']} "
                        f"(threshold: {alert['threshold']} {alert['unit']})"
                    ),
                    "source": "automated_sensor",
                    "timestamp": time.time(),
                }
            )
        return items

    def _gather_report_evidence(self, citizen_reports) -> list:
        items = []
        for report in citizen_reports:
            desc = f"Citizen report {report['report_id']}: \"{report['description']}\""
            if report.get("photo_available"):
                desc += " [PHOTO ATTACHED]"
            items.append(
                {
                    "type": "citizen_report",
                    "description": desc,
                    "source": "citizen_portal",
                    "timestamp": time.time(),
                }
            )
        return items

    def _gather_metadata_evidence(self, content) -> list:
        return [
            {
                "type": "geo_location",
                "description": (
                    f"Location: {content['location_description']} "
                    f"(key: {content['location_key']})"
                ),
                "source": "location_database",
                "timestamp": time.time(),
            },
            {
                "type": "detection_metadata",
                "description": (
                    f"Detection confidence: {content['confidence']}, "
                    f"Classification: {content['waste_type']}/{content['severity']}"
                ),
                "source": "assessment_agent",
                "timestamp": time.time(),
            },
        ]

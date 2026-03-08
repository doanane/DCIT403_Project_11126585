from src.core.agent import Agent
from src.core.message import Message, Performative
from src.beliefs.incident_belief import IncidentDatabase


HAZARDOUS_SENSOR_TYPES = {"chemical", "radiation", "air_quality"}
CHEMICAL_SEVERITY_THRESHOLDS = {
    "critical": 200.0,
    "high": 100.0,
    "medium": 50.0,
}
TEMPERATURE_SEVERITY_THRESHOLDS = {
    "critical": 120.0,
    "high": 80.0,
    "medium": 50.0,
}


class AssessmentAgent(Agent):
    def __init__(self, name: str, agent_system):
        super().__init__(name, agent_system)
        self.beliefs["pending_assessments"] = {}
        self.beliefs["classified_incidents"] = {}
        self.beliefs["classification_rules"] = {
            "chemical": "hazardous",
            "radiation": "hazardous",
            "air_quality": "hazardous",
            "temperature": "requires_context",
            "visual": "requires_context",
        }

    def select_plan(self, percept):
        if isinstance(percept, Message):
            if percept.performative == Performative.INCIDENT_DETECTED:
                return self._plan_assess_incident
            if percept.performative == Performative.INCIDENT_UPDATE:
                return self._plan_handle_update
        return None

    def _plan_assess_incident(self, message: Message):
        content = message.content
        incident_id = content["incident_id"]
        sensor_types = content.get("sensor_types", [])
        sensor_alerts = content.get("sensor_alerts", [])
        citizen_reports = content.get("citizen_reports", [])
        confidence = content.get("confidence", 0.0)

        self.beliefs["pending_assessments"][incident_id] = content

        waste_type, severity = self._classify(sensor_types, sensor_alerts, citizen_reports)

        self.beliefs["classified_incidents"][incident_id] = {
            "waste_type": waste_type,
            "severity": severity,
            "confidence": confidence,
        }

        print(
            f"    [AssessmentAgent] ACT: Incident {incident_id} assessed -> "
            f"Waste type: {waste_type.upper()}, Severity: {severity.upper()}"
        )

        classification_content = {
            "incident_id": incident_id,
            "location_key": content["location_key"],
            "location_description": content["location_description"],
            "waste_type": waste_type,
            "severity": severity,
            "confidence": confidence,
            "sensor_alerts": sensor_alerts,
            "citizen_reports": citizen_reports,
        }

        self.send("EvidenceAgent", Performative.INCIDENT_CLASSIFIED, classification_content)
        print(
            f"    [AssessmentAgent] SEND -> EvidenceAgent: "
            f"INCIDENT_CLASSIFIED [{incident_id}] ({waste_type}/{severity})"
        )

        self.send("EnforcementAgent", Performative.DISPATCH_REQUEST, classification_content)
        print(
            f"    [AssessmentAgent] SEND -> EnforcementAgent: "
            f"DISPATCH_REQUEST [{incident_id}] ({waste_type}/{severity})"
        )

    def _plan_handle_update(self, message: Message):
        content = message.content
        incident_id = content["incident_id"]
        new_confidence = content.get("confidence", 0.0)
        if incident_id in self.beliefs["classified_incidents"]:
            self.beliefs["classified_incidents"][incident_id]["confidence"] = new_confidence
            print(
                f"    [AssessmentAgent] ACT: Incident {incident_id} confidence updated to {new_confidence}."
            )

    def _classify(self, sensor_types, sensor_alerts, citizen_reports):
        waste_type = self._determine_waste_type(sensor_types, citizen_reports)
        severity = self._determine_severity(waste_type, sensor_alerts, citizen_reports)
        return waste_type, severity

    def _determine_waste_type(self, sensor_types, citizen_reports) -> str:
        rules = self.beliefs["classification_rules"]
        for stype in sensor_types:
            rule_result = rules.get(stype, "unknown")
            if rule_result == "hazardous":
                return "hazardous"

        report_texts = " ".join(
            r.get("description", "").lower() for r in citizen_reports
        )
        hazardous_keywords = [
            "chemical", "toxic", "smell", "fumes", "barrel",
            "drum", "liquid", "acid", "gas", "hazardous",
        ]
        solid_keywords = [
            "rubble", "debris", "construction", "concrete", "rubbish",
            "garbage", "trash", "furniture", "mattress",
        ]
        haz_score = sum(1 for kw in hazardous_keywords if kw in report_texts)
        solid_score = sum(1 for kw in solid_keywords if kw in report_texts)

        if haz_score > solid_score:
            return "hazardous"
        if solid_score > 0:
            return "non_hazardous"

        if sensor_types:
            return "unknown_requires_investigation"

        return "non_hazardous"

    def _determine_severity(self, waste_type, sensor_alerts, citizen_reports) -> str:
        max_severity_score = 0

        for alert in sensor_alerts:
            stype = alert.get("type", "")
            value = alert.get("value", 0.0)

            if stype == "chemical":
                if value > CHEMICAL_SEVERITY_THRESHOLDS["critical"]:
                    max_severity_score = max(max_severity_score, 4)
                elif value > CHEMICAL_SEVERITY_THRESHOLDS["high"]:
                    max_severity_score = max(max_severity_score, 3)
                elif value > CHEMICAL_SEVERITY_THRESHOLDS["medium"]:
                    max_severity_score = max(max_severity_score, 2)
                else:
                    max_severity_score = max(max_severity_score, 1)

            elif stype == "temperature":
                if value > TEMPERATURE_SEVERITY_THRESHOLDS["critical"]:
                    max_severity_score = max(max_severity_score, 4)
                elif value > TEMPERATURE_SEVERITY_THRESHOLDS["high"]:
                    max_severity_score = max(max_severity_score, 3)
                elif value > TEMPERATURE_SEVERITY_THRESHOLDS["medium"]:
                    max_severity_score = max(max_severity_score, 2)
                else:
                    max_severity_score = max(max_severity_score, 1)

            elif stype in ("air_quality", "radiation"):
                ratio = value / max(alert.get("threshold", 1), 1)
                if ratio > 3:
                    max_severity_score = max(max_severity_score, 4)
                elif ratio > 2:
                    max_severity_score = max(max_severity_score, 3)
                else:
                    max_severity_score = max(max_severity_score, 2)

        if len(citizen_reports) >= 2:
            max_severity_score = max(max_severity_score, 2)

        if waste_type == "hazardous" and max_severity_score == 0:
            max_severity_score = 2

        severity_map = {0: "low", 1: "low", 2: "medium", 3: "high", 4: "critical"}
        return severity_map.get(max_severity_score, "medium")

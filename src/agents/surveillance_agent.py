import time
import uuid

from src.core.agent import Agent
from src.core.message import Message, Performative
from src.beliefs.incident_belief import (
    Incident,
    IncidentDatabase,
    SensorAlert,
    CitizenReport,
)
from src.beliefs.location_belief import LocationDatabase

SENSOR_CONFIRMATION_THRESHOLD = 2
CITIZEN_REPORT_THRESHOLD = 2


class SurveillanceAgent(Agent):
    def __init__(self, name: str, agent_system):
        super().__init__(name, agent_system)
        self.beliefs["incidents"] = IncidentDatabase()
        self.beliefs["locations"] = LocationDatabase()
        self.beliefs["pending_sensor_alerts"] = {}
        self.beliefs["pending_citizen_reports"] = {}
        self.beliefs["dispatched_incident_ids"] = set()

    def select_plan(self, percept):
        if isinstance(percept, Message):
            if percept.performative == Performative.SENSOR_ALERT:
                return self._plan_handle_sensor_alert
            if percept.performative == Performative.CITIZEN_REPORT:
                return self._plan_handle_citizen_report
            if percept.performative == Performative.RESPONSE_UPDATE:
                return self._plan_handle_response_update
        return None

    def _plan_handle_sensor_alert(self, message: Message):
        content = message.content
        location_key = content["location_key"]
        alert = SensorAlert(
            alert_id=content["alert_id"],
            sensor_id=content["sensor_id"],
            sensor_type=content["sensor_type"],
            location_key=location_key,
            location_description=content["location_description"],
            reading_value=content["reading_value"],
            unit=content["unit"],
            threshold=content["threshold"],
            timestamp=content["timestamp"],
        )

        pending = self.beliefs["pending_sensor_alerts"]
        if location_key not in pending:
            pending[location_key] = []
        pending[location_key].append(alert)

        count = len(pending[location_key])
        print(
            f"    [SurveillanceAgent] ACT: Alert {alert.alert_id} stored. "
            f"Location {location_key} has {count}/{SENSOR_CONFIRMATION_THRESHOLD} sensor confirmation(s)."
        )

        if count >= SENSOR_CONFIRMATION_THRESHOLD:
            self._create_or_update_incident_from_sensors(location_key)

    def _plan_handle_citizen_report(self, message: Message):
        content = message.content
        location_key = content["location_key"]
        report = CitizenReport(
            report_id=content["report_id"],
            location_key=location_key,
            location_description=content["location_description"],
            description=content["description"],
            photo_available=content.get("photo_available", False),
            timestamp=content["timestamp"],
        )

        pending_reports = self.beliefs["pending_citizen_reports"]
        if location_key not in pending_reports:
            pending_reports[location_key] = []
        pending_reports[location_key].append(report)

        existing = self.beliefs["incidents"].get_by_location(location_key)
        if existing:
            existing.citizen_reports.append(report)
            print(
                f"    [SurveillanceAgent] ACT: Report {report.report_id} correlated "
                f"with existing incident {existing.incident_id}. "
                f"Confidence now: {existing.confidence_level()}"
            )
            if existing.incident_id not in self.beliefs["dispatched_incident_ids"]:
                self._notify_assessment_update(existing)
        else:
            report_count = len(pending_reports[location_key])
            print(
                f"    [SurveillanceAgent] ACT: Report {report.report_id} stored. "
                f"Location {location_key} has {report_count}/{CITIZEN_REPORT_THRESHOLD} report(s)."
            )
            if report_count >= CITIZEN_REPORT_THRESHOLD:
                self._create_incident_from_reports(location_key)

    def _plan_handle_response_update(self, message: Message):
        content = message.content
        incident_id = content["incident_id"]
        new_status = content["status"]
        self.beliefs["incidents"].update_status(incident_id, new_status)
        print(
            f"    [SurveillanceAgent] ACT: Incident {incident_id} status updated to '{new_status}'."
        )

    def _create_or_update_incident_from_sensors(self, location_key: str):
        db = self.beliefs["incidents"]
        pending = self.beliefs["pending_sensor_alerts"][location_key]
        loc_db = self.beliefs["locations"]
        loc_db.record_incident(location_key, time.time())

        existing = db.get_by_location(location_key)
        if existing:
            for alert in pending:
                if alert not in existing.sensor_alerts:
                    existing.sensor_alerts.append(alert)
            print(
                f"    [SurveillanceAgent] ACT: Additional sensor data added to {existing.incident_id}."
            )
            return

        incident_id = f"INC-{str(uuid.uuid4())[:4].upper()}"
        location_desc = pending[0].location_description
        incident = Incident(
            incident_id=incident_id,
            location_key=location_key,
            location_description=location_desc,
            sensor_alerts=list(pending),
        )
        pending_reports = self.beliefs["pending_citizen_reports"].get(location_key, [])
        incident.citizen_reports = list(pending_reports)
        db.add_incident(incident)

        is_hotspot = loc_db.is_hotspot(location_key)
        hotspot_note = " [KNOWN HOTSPOT]" if is_hotspot else ""
        print(
            f"    [SurveillanceAgent] ACT: Incident threshold met! "
            f"Incident {incident_id} created at {location_key}{hotspot_note}. "
            f"Confidence: {incident.confidence_level()}"
        )
        self._dispatch_to_assessment(incident)

    def _create_incident_from_reports(self, location_key: str):
        db = self.beliefs["incidents"]
        pending_reports = self.beliefs["pending_citizen_reports"][location_key]
        loc_db = self.beliefs["locations"]
        loc_db.record_incident(location_key, time.time())

        incident_id = f"INC-{str(uuid.uuid4())[:4].upper()}"
        location_desc = pending_reports[0].location_description
        incident = Incident(
            incident_id=incident_id,
            location_key=location_key,
            location_description=location_desc,
            citizen_reports=list(pending_reports),
        )
        pending_sensors = self.beliefs["pending_sensor_alerts"].get(location_key, [])
        incident.sensor_alerts = list(pending_sensors)
        db.add_incident(incident)

        is_hotspot = loc_db.is_hotspot(location_key)
        hotspot_note = " [KNOWN HOTSPOT]" if is_hotspot else ""
        print(
            f"    [SurveillanceAgent] ACT: Multiple citizen reports confirmed. "
            f"Incident {incident_id} created at {location_key}{hotspot_note}. "
            f"Confidence: {incident.confidence_level()}"
        )
        self._dispatch_to_assessment(incident)

    def _dispatch_to_assessment(self, incident: Incident):
        self.beliefs["dispatched_incident_ids"].add(incident.incident_id)
        content = {
            "incident_id": incident.incident_id,
            "location_key": incident.location_key,
            "location_description": incident.location_description,
            "sensor_types": incident.sensor_types_present(),
            "sensor_alerts": [
                {
                    "type": a.sensor_type,
                    "value": a.reading_value,
                    "unit": a.unit,
                    "threshold": a.threshold,
                }
                for a in incident.sensor_alerts
            ],
            "citizen_reports": [
                {
                    "report_id": r.report_id,
                    "description": r.description,
                    "photo_available": r.photo_available,
                }
                for r in incident.citizen_reports
            ],
            "confidence": incident.confidence_level(),
            "detected_at": incident.detected_at,
        }
        msg = self.send("AssessmentAgent", Performative.INCIDENT_DETECTED, content)
        print(
            f"    [SurveillanceAgent] SEND -> AssessmentAgent: "
            f"INCIDENT_DETECTED [{incident.incident_id}] "
            f"(sensors: {incident.sensor_types_present()}, "
            f"reports: {len(incident.citizen_reports)})"
        )

    def _notify_assessment_update(self, incident: Incident):
        content = {
            "incident_id": incident.incident_id,
            "additional_reports": len(incident.citizen_reports),
            "confidence": incident.confidence_level(),
        }
        self.send("AssessmentAgent", Performative.INCIDENT_UPDATE, content)
        print(
            f"    [SurveillanceAgent] SEND -> AssessmentAgent: "
            f"INCIDENT_UPDATE [{incident.incident_id}] "
            f"(updated confidence: {incident.confidence_level()})"
        )

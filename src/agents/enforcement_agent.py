import time

from src.core.agent import Agent
from src.core.message import Message, Performative
from src.beliefs.authority_belief import AuthorityDatabase, DispatchRecord

ESCALATION_TIMEOUT_STEPS = 5


class EnforcementAgent(Agent):
    def __init__(self, name: str, agent_system):
        super().__init__(name, agent_system)
        self.beliefs["authority_db"] = AuthorityDatabase()
        self.beliefs["pending_dispatches"] = {}
        self.beliefs["received_evidence"] = {}
        self.beliefs["resolved_incidents"] = set()
        self.beliefs["case_files"] = {}

    def select_plan(self, percept):
        if isinstance(percept, Message):
            if percept.performative == Performative.DISPATCH_REQUEST:
                return self._plan_process_dispatch_request
            if percept.performative == Performative.EVIDENCE_PACKAGE:
                return self._plan_attach_evidence
            if percept.performative == Performative.ESCALATION_ALERT:
                return self._plan_escalate
        return None

    def _plan_process_dispatch_request(self, message: Message):
        content = message.content
        incident_id = content["incident_id"]
        waste_type = content["waste_type"]
        severity = content["severity"]
        location_desc = content["location_description"]

        self.beliefs["pending_dispatches"][incident_id] = {
            "content": content,
            "received_at": time.time(),
            "evidence_attached": False,
            "dispatched": False,
        }

        auth_db = self.beliefs["authority_db"]
        selected_authorities = auth_db.select_authority(waste_type, severity)

        print(
            f"    [EnforcementAgent] ACT: Dispatch request received for {incident_id}. "
            f"Evaluating required authorities for {waste_type}/{severity} case..."
        )

        dispatch_records = []
        for auth_id in selected_authorities:
            authority = auth_db.get_authority(auth_id)
            record = DispatchRecord(
                incident_id=incident_id,
                authority_id=auth_id,
                authority_name=authority.name,
            )
            auth_db.record_dispatch(record)
            dispatch_records.append(record)
            print(
                f"    [EnforcementAgent] ACT: Dispatching {authority.name} "
                f"to {location_desc}. Contact: {authority.contact}"
            )

        self.beliefs["pending_dispatches"][incident_id]["dispatched"] = True
        self.beliefs["pending_dispatches"][incident_id]["dispatch_records"] = dispatch_records
        self.beliefs["pending_dispatches"][incident_id]["dispatch_time"] = time.time()
        self.beliefs["pending_dispatches"][incident_id]["dispatch_step"] = 0

        if incident_id not in self.beliefs["case_files"]:
            self.beliefs["case_files"][incident_id] = {
                "incident_id": incident_id,
                "waste_type": waste_type,
                "severity": severity,
                "location": location_desc,
                "authorities": [a.authority_name for a in dispatch_records],
                "status": "dispatched",
                "evidence": None,
            }

        self.send(
            "SurveillanceAgent",
            Performative.RESPONSE_UPDATE,
            {"incident_id": incident_id, "status": "dispatched"},
        )
        print(
            f"    [EnforcementAgent] SEND -> SurveillanceAgent: "
            f"RESPONSE_UPDATE [{incident_id}] status=dispatched"
        )

    def _plan_attach_evidence(self, message: Message):
        content = message.content
        incident_id = content["incident_id"]
        package_id = content["package_id"]
        item_count = content["item_count"]

        self.beliefs["received_evidence"][incident_id] = content

        if incident_id in self.beliefs["case_files"]:
            self.beliefs["case_files"][incident_id]["evidence"] = package_id
            self.beliefs["case_files"][incident_id]["status"] = "evidence_attached"

        print(
            f"    [EnforcementAgent] ACT: Evidence package {package_id} "
            f"attached to case {incident_id}. "
            f"{item_count} evidence item(s) on record."
        )
        self._print_case_summary(incident_id)

    def _plan_escalate(self, message: Message):
        content = message.content
        incident_id = content["incident_id"]
        reason = content.get("reason", "No response from dispatched authority")

        auth_db = self.beliefs["authority_db"]
        regional = auth_db.get_authority("REGIONAL")

        escalation_record = DispatchRecord(
            incident_id=incident_id,
            authority_id="REGIONAL",
            authority_name=regional.name,
        )
        auth_db.record_dispatch(escalation_record)

        if incident_id in self.beliefs["case_files"]:
            self.beliefs["case_files"][incident_id]["status"] = "escalated"
            self.beliefs["case_files"][incident_id]["authorities"].append(regional.name)

        print(
            f"    [EnforcementAgent] ACT: ESCALATING incident {incident_id}. "
            f"Reason: {reason}"
        )
        print(
            f"    [EnforcementAgent] ACT: {regional.name} alerted. "
            f"Contact: {regional.contact}"
        )

    def check_and_escalate_overdue(self, current_step: int):
        for incident_id, dispatch_info in list(self.beliefs["pending_dispatches"].items()):
            if incident_id in self.beliefs["resolved_incidents"]:
                continue
            if not dispatch_info.get("dispatched"):
                continue
            evidence = self.beliefs["received_evidence"].get(incident_id)
            if evidence is None:
                continue
            case = self.beliefs["case_files"].get(incident_id, {})
            if case.get("status") != "evidence_attached":
                continue
            if dispatch_info.get("dispatch_step") == 0:
                dispatch_info["dispatch_step"] = current_step
            steps_since_dispatch = current_step - dispatch_info["dispatch_step"]
            if steps_since_dispatch >= ESCALATION_TIMEOUT_STEPS:
                print(
                    f"    [EnforcementAgent] ACT: Incident {incident_id} has no authority "
                    f"response after {steps_since_dispatch} steps. Initiating escalation."
                )
                escalate_msg = Message(
                    sender="EnforcementAgent",
                    receiver="EnforcementAgent",
                    performative=Performative.ESCALATION_ALERT,
                    content={
                        "incident_id": incident_id,
                        "reason": (
                            f"No response received after {steps_since_dispatch} simulation steps."
                        ),
                    },
                )
                self._plan_escalate(escalate_msg)
                self.beliefs["resolved_incidents"].add(incident_id)

    def _print_case_summary(self, incident_id: str):
        case = self.beliefs["case_files"].get(incident_id)
        if not case:
            return
        print(f"    [EnforcementAgent] --- Case Summary for {incident_id} ---")
        print(f"      Location  : {case['location']}")
        print(f"      Waste Type: {case['waste_type']}")
        print(f"      Severity  : {case['severity']}")
        print(f"      Status    : {case['status']}")
        print(f"      Authorities: {', '.join(case['authorities'])}")
        print(f"      Evidence  : {case['evidence']}")
        print(f"    [EnforcementAgent] ----------------------------------------")

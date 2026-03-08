import time

from src.core.agent_system import AgentSystem
from src.agents.surveillance_agent import SurveillanceAgent
from src.agents.assessment_agent import AssessmentAgent
from src.agents.evidence_agent import EvidenceAgent
from src.agents.enforcement_agent import EnforcementAgent
from src.environment.sensor_network import SensorNetwork
from src.environment.report_generator import ReportGenerator

TOTAL_STEPS = 16
STEP_DELAY_SECONDS = 0.4


def _separator(label=""):
    width = 70
    if label:
        side = (width - len(label) - 2) // 2
        print("=" * side + f" {label} " + "=" * (width - side - len(label) - 2))
    else:
        print("=" * width)


class WasteWatchSimulator:
    def __init__(self):
        self.agent_system = AgentSystem()
        self.surveillance = SurveillanceAgent("SurveillanceAgent", self.agent_system)
        self.assessment = AssessmentAgent("AssessmentAgent", self.agent_system)
        self.evidence = EvidenceAgent("EvidenceAgent", self.agent_system)
        self.enforcement = EnforcementAgent("EnforcementAgent", self.agent_system)

        for agent in [self.surveillance, self.assessment, self.evidence, self.enforcement]:
            self.agent_system.register(agent)

        self.sensor_network = SensorNetwork()
        self.report_generator = ReportGenerator()
        self.agents_in_order = [
            self.surveillance,
            self.assessment,
            self.evidence,
            self.enforcement,
        ]

    def _inject_environment_events(self, step: int):
        sensor_msgs = self.sensor_network.get_events_for_step(step)
        report_msgs = self.report_generator.get_events_for_step(step)
        all_msgs = sensor_msgs + report_msgs
        if all_msgs:
            for msg in all_msgs:
                self.agent_system.deliver(msg)
        return len(all_msgs)

    def _run_agent_cycles(self, step: int):
        for agent in self.agents_in_order:
            had_percepts = len(agent.inbox) > 0
            if had_percepts:
                print(
                    f"  [{agent.name}] PERCEIVE: "
                    f"{len(agent.inbox)} incoming message(s)"
                )
                agent_plan_map = {
                    "SurveillanceAgent": [
                        "handle_sensor_alert",
                        "handle_citizen_report",
                        "handle_response_update",
                    ],
                    "AssessmentAgent": [
                        "assess_incident",
                        "handle_update",
                    ],
                    "EvidenceAgent": [
                        "collect_evidence",
                    ],
                    "EnforcementAgent": [
                        "process_dispatch_request",
                        "attach_evidence",
                        "escalate",
                    ],
                }
                plans_available = agent_plan_map.get(agent.name, [])
                print(
                    f"  [{agent.name}] DELIBERATE: Selecting plan from "
                    f"{len(plans_available)} available plan(s)."
                )
            agent.run_cycle(step)

        self.enforcement.check_and_escalate_overdue(step)

    def _print_step_header(self, step: int):
        _separator(f"STEP {step:02d}")

    def _print_final_report(self):
        _separator("FINAL INCIDENT REPORT")
        print()

        all_incidents = self.surveillance.beliefs["incidents"].all_incidents()
        if not all_incidents:
            print("  No incidents were recorded in this simulation run.")
            return

        for inc in all_incidents:
            case = self.enforcement.beliefs["case_files"].get(inc.incident_id, {})
            evidence_pkg = self.evidence.beliefs["compiled_packages"].get(inc.incident_id, {})
            assessment = self.assessment.beliefs["classified_incidents"].get(inc.incident_id, {})
            print(f"  Incident ID   : {inc.incident_id}")
            print(f"  Location      : {inc.location_description}")
            print(f"  Status        : {inc.status}")
            print(f"  Waste Type    : {assessment.get('waste_type', 'N/A')}")
            print(f"  Severity      : {assessment.get('severity', 'N/A')}")
            print(f"  Sensor Alerts : {len(inc.sensor_alerts)} alert(s)")
            print(f"  Citizen Reports: {len(inc.citizen_reports)} report(s)")
            print(f"  Confidence    : {inc.confidence_level()}")
            if evidence_pkg:
                print(f"  Evidence Pkg  : {evidence_pkg.get('package_id', 'N/A')} "
                      f"({evidence_pkg.get('item_count', 0)} items)")
            auth_list = case.get("authorities", [])
            if auth_list:
                print(f"  Authorities   : {', '.join(auth_list)}")
            print()

    def run(self):
        _separator()
        print("   WASTEWATCH - Intelligent Illegal Waste Dumping Detection System")
        print("   Designed using the Prometheus Methodology")
        print("   Student ID: 11126585 | DCIT403 Semester Project")
        _separator()
        print()
        print("  Registering agents:")
        for agent in self.agents_in_order:
            print(f"    + {agent.name}")
        print()
        print("  Environment online:")
        print("    + SensorNetwork  (4 sensors scheduled across simulation)")
        print("    + CitizenPortal  (4 reports scheduled across simulation)")
        print()
        print("  Scenario overview:")
        print("    Scenario 1 (Steps 1-4) : Chemical hazardous waste at LOC-A")
        print("    Scenario 2 (Steps 5-9) : Construction debris at LOC-B")
        print("    Scenario 3 (Steps 7-15): Air quality degradation at LOC-C")
        print()
        _separator("SIMULATION START")
        print()
        time.sleep(0.3)

        for step in range(1, TOTAL_STEPS + 1):
            self._print_step_header(step)
            env_count = self._inject_environment_events(step)
            if env_count == 0 and all(len(a.inbox) == 0 for a in self.agents_in_order):
                print("  [Environment] No events this step.")
                enforcement_has_work = any(
                    info.get("dispatched")
                    and self.enforcement.beliefs["received_evidence"].get(inc_id) is not None
                    and self.enforcement.beliefs["case_files"].get(inc_id, {}).get("status") == "evidence_attached"
                    for inc_id, info in self.enforcement.beliefs["pending_dispatches"].items()
                    if inc_id not in self.enforcement.beliefs["resolved_incidents"]
                )
                if not enforcement_has_work:
                    print()
                    time.sleep(STEP_DELAY_SECONDS)
                    continue
            self._run_agent_cycles(step)
            print()
            time.sleep(STEP_DELAY_SECONDS)

        _separator()
        self._print_final_report()
        _separator()
        print()
        print("  Simulation complete.")
        print()

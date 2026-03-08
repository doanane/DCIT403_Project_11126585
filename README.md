# WasteWatch
## Intelligent Illegal Waste Dumping Detection and Enforcement Coordination System

**Student ID:** 11126585
**Course:** DCIT 403 - Intelligent Agent Systems
**Methodology:** Prometheus (Padgham & Winikoff, 2004)
**Language:** Python 3

---

## Project Overview

WasteWatch is a multi-agent system that detects illegal waste dumping incidents through an automated sensor network and citizen reports, classifies waste by type and severity, compiles tamper-evident evidence, and dispatches the correct enforcement authority. If no authority responds within the timeout window, the system escalates the case to a regional enforcement unit.

The system implements the complete Prometheus methodology across five phases and demonstrates the following intelligent agent properties:
- **Reactivity:** Agents respond immediately to sensor alerts and citizen reports
- **Proactivity:** The EnforcementAgent proactively monitors for unresponded cases and escalates
- **Social ability:** Four specialised agents communicate through structured messages

---

## System Architecture

```
SensorNetwork --------> SurveillanceAgent -----> AssessmentAgent
CitizenPortal -------->                               |
                                                   /     \
                                          EvidenceAgent  EnforcementAgent
                                                   \     /
                                          EVIDENCE_PACKAGE
                                                      |
                                            -> Authority Dispatch
                                            -> Escalation if overdue
```

---

## Agents

| Agent | Role |
|---|---|
| SurveillanceAgent | Monitors environment, correlates signals, creates incidents |
| AssessmentAgent | Classifies waste type and severity using rules and keywords |
| EvidenceAgent | Collects and compiles tamper-evident evidence packages |
| EnforcementAgent | Dispatches authorities, tracks responses, escalates overdue cases |

---

## Setup

### Prerequisites

- Python 3.8 or higher
- The `.venv` virtual environment directory is already present in the project root

### Activating the Virtual Environment

**Windows (Command Prompt):**
```
.venv\Scripts\activate
```

**Windows (PowerShell):**
```
.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```
source .venv/bin/activate
```

### Installing Dependencies

The system uses only the Python standard library. No additional packages are required.

```
pip install -r requirements.txt
```

### Running the Simulation

```
python main.py
```

---

## Project Structure

```
DCIT403_Project_11126585/
|
+-- main.py                          Entry point
+-- requirements.txt                 Python dependencies
+-- README.md                        This file
|
+-- src/
|   +-- core/
|   |   +-- agent.py                 Abstract base Agent class (perceive/decide/act)
|   |   +-- agent_system.py          Message routing and agent registry
|   |   +-- message.py               Message dataclass and Performative enum
|   |
|   +-- agents/
|   |   +-- surveillance_agent.py    SurveillanceAgent implementation
|   |   +-- assessment_agent.py      AssessmentAgent implementation
|   |   +-- evidence_agent.py        EvidenceAgent implementation
|   |   +-- enforcement_agent.py     EnforcementAgent implementation
|   |
|   +-- beliefs/
|   |   +-- incident_belief.py       Incident, SensorAlert, CitizenReport, IncidentDatabase
|   |   +-- location_belief.py       Location, HotspotRecord, LocationDatabase
|   |   +-- authority_belief.py      Authority, DispatchRecord, AuthorityDatabase
|   |
|   +-- environment/
|   |   +-- sensor_network.py        Simulated sensor network (4 scheduled events)
|   |   +-- report_generator.py      Simulated citizen report system (4 reports)
|   |
|   +-- simulation/
|       +-- simulator.py             WasteWatchSimulator orchestration class
|
+-- docs/
|   +-- phase1_system_specification.md
|   +-- phase2_architectural_design.md
|   +-- phase3_interaction_design.md
|   +-- phase4_detailed_design.md
|   +-- phase5_report.md
|
+-- diagrams/
    +-- goal_hierarchy.txt
    +-- system_overview.txt
    +-- acquaintance_diagram.txt
    +-- interaction_diagram_scenario1.txt
    +-- interaction_diagram_scenario2.txt
    +-- interaction_diagram_scenario3.txt
    +-- capability_overview_surveillance.txt
    +-- capability_overview_assessment.txt
    +-- capability_overview_evidence.txt
    +-- capability_overview_enforcement.txt
```

---

## Simulation Scenarios

The simulation runs three scenarios across 16 steps (0.4 seconds per step):

**Scenario 1 (Steps 1-7):** Chemical hazardous waste at an abandoned industrial site.
Two sensors (chemical: 157 ppm, temperature: 134 C) trigger the SurveillanceAgent.
The AssessmentAgent classifies the incident as HAZARDOUS/CRITICAL.
EPA and HAZMAT are dispatched. The incident is subsequently escalated after 5 steps with no response.

**Scenario 2 (Steps 5-11):** Construction debris at a roadside.
Two citizen reports describe rubble and debris at the same location.
Keyword analysis classifies the incident as NON_HAZARDOUS/MEDIUM.
The local environmental officer is dispatched. The incident is subsequently escalated.

**Scenario 3 (Steps 7-13):** Air quality degradation at a riverbank.
Two air quality sensors exceed the AQI threshold by a factor of three.
A late citizen report corroborates the incident and raises confidence from 0.6 to 0.8.
EPA and HAZMAT are dispatched. The incident is subsequently escalated.

---

## Key Design Decisions

**Why step-based simulation instead of threading?**
A step-based simulation makes the perceive-decide-act cycle explicit and traceable in the console output. Threading would introduce non-determinism that would obscure the Prometheus design demonstration.

**Why separate EvidenceAgent and EnforcementAgent?**
These agents represent genuinely different organisational concerns: forensic evidence management (chain of custody, evidence integrity) and field enforcement (authority selection, response tracking). Separating them makes the system more maintainable.

**Why four agents instead of one?**
The domain naturally separates into four roles that are loosely coupled. A single agent would conflate detection logic, classification reasoning, evidentiary procedure, and enforcement policy in ways that would make the system harder to understand, test, and modify.

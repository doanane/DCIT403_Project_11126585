# Phase 2 - Architectural Design
## WasteWatch: Intelligent Illegal Waste Dumping Detection and Enforcement Coordination System

---

## 1. Agent Types

### How many agents and why?

The system uses **four distinct agent types**. The decision to use multiple agents rather than a single monolithic agent follows the Prometheus guideline that functionalities which are loosely coupled, address different concerns, or represent different organisational roles should be separated into distinct agents (Padgham & Winikoff, 2004, Chapter 5).

| Agent | Count | Rationale |
|---|---|---|
| SurveillanceAgent | 1 | Boundary agent between the environment and the rest of the system. Handles all external percepts. |
| AssessmentAgent | 1 | Domain reasoning agent. Applies classification rules. Isolated from sensing so classification logic can evolve independently. |
| EvidenceAgent | 1 | Data stewardship agent. Concerned only with collecting, timestamping, and preserving evidence. Separation ensures evidence integrity. |
| EnforcementAgent | 1 | Action agent. Translates classification decisions into real-world dispatch orders. Manages response tracking and escalation. |

**Justification for four agents over one:**

A single agent approach would conflate four very different types of reasoning: environmental monitoring (reactive, event-driven), domain classification (rule-based deliberation), evidentiary procedure (data gathering and chain-of-custody), and enforcement coordination (goal-directed, monitoring over time). By separating these into four agents, each agent can be designed, modified, and validated independently. The communication protocol between agents also makes the information flow explicit and auditable, which is important for a law enforcement application.

---

## 2. Grouping Functionalities

The following table maps each functionality defined in Phase 1 to the agent responsible for it.

| Functionality | Assigned Agent | Reasoning |
|---|---|---|
| F1 - Monitor sensor network | SurveillanceAgent | Direct environment interface |
| F2 - Receive citizen reports | SurveillanceAgent | Direct environment interface |
| F3 - Correlate sensor alerts | SurveillanceAgent | Accumulation of sensor data requires local state |
| F4 - Correlate citizen reports | SurveillanceAgent | Accumulation of report data requires local state |
| F5 - Create incident record | SurveillanceAgent | Incident creation follows detection threshold logic |
| F6 - Track confidence levels | SurveillanceAgent | Confidence depends on all accumulated signals |
| F7 - Identify hotspots | SurveillanceAgent | Hotspot detection requires location history |
| F8 - Classify waste type | AssessmentAgent | Classification is domain reasoning, not detection |
| F9 - Determine severity | AssessmentAgent | Severity requires rule application across sensor values |
| F10 - Context-conditioned plan selection | AssessmentAgent | Plan selection is an assessment-level decision |
| F11 - Collect evidence items | EvidenceAgent | Evidence collection is a distinct procedural concern |
| F12 - Compile evidence package | EvidenceAgent | Package compilation is a distinct procedural concern |
| F13 - Select enforcement authority | EnforcementAgent | Authority selection depends on dispatch policy |
| F14 - Dispatch authority | EnforcementAgent | Dispatch is an action taken by the enforcement agent |
| F15 - Track dispatch status | EnforcementAgent | Status tracking is a persistent enforcement concern |
| F16 - Detect overdue responses | EnforcementAgent | Timeout logic requires persistent tracking of dispatch time |
| F17 - Escalate overdue incidents | EnforcementAgent | Escalation is an enforcement-level action |
| F18 - Update incident status | SurveillanceAgent / EnforcementAgent | Both update status at different pipeline stages |
| F19 - Produce final incident report | Simulator (external) | Reporting is a simulation output function |

---

## 3. Acquaintance Diagram

The acquaintance diagram shows which agents know about and communicate with each other.

```
  +-------------------+         +-------------------+
  |  SensorNetwork    |         |  CitizenPortal    |
  |  (Environment)    |         |  (Environment)    |
  +--------+----------+         +--------+----------+
           |  SENSOR_ALERT               |  CITIZEN_REPORT
           |                             |
           v                             v
  +---------------------------------------------------+
  |              SurveillanceAgent                    |
  |   (Perceives environment, creates incidents)      |
  +----------------------+----------------------------+
                         |
                         | INCIDENT_DETECTED
                         | INCIDENT_UPDATE
                         v
  +---------------------------------------------------+
  |               AssessmentAgent                     |
  |   (Classifies waste type and severity)            |
  +----------+---------------------+-----------------+
             |                     |
             | INCIDENT_CLASSIFIED | DISPATCH_REQUEST
             v                     v
  +-----------------+   +-------------------------+
  |  EvidenceAgent  |   |    EnforcementAgent     |
  |  (Compiles      |   |  (Dispatches authority, |
  |   evidence)     |   |   tracks response,      |
  +---------+-------+   |   escalates if overdue) |
            |           +----------+--------------+
            | EVIDENCE_PACKAGE     |
            +--------------------->|
                                   |
                                   | RESPONSE_UPDATE
                                   v
                        SurveillanceAgent
```

**Information flow summary:**

- SurveillanceAgent receives from: SensorNetwork, CitizenPortal, EnforcementAgent
- SurveillanceAgent sends to: AssessmentAgent
- AssessmentAgent receives from: SurveillanceAgent
- AssessmentAgent sends to: EvidenceAgent, EnforcementAgent
- EvidenceAgent receives from: AssessmentAgent
- EvidenceAgent sends to: EnforcementAgent
- EnforcementAgent receives from: AssessmentAgent, EvidenceAgent
- EnforcementAgent sends to: SurveillanceAgent

---

## 4. Agent Descriptors

### SurveillanceAgent

| Property | Description |
|---|---|
| Name | SurveillanceAgent |
| Responsibilities | Detect incidents from sensor alerts and citizen reports. Correlate multiple signals from the same location. Create and update incident records. Track confidence levels. Record hotspots. |
| Goals handled | G1 (Detect incidents), G1.1-G1.5 |
| Plans | handle_sensor_alert, handle_citizen_report, handle_response_update |
| Beliefs maintained | IncidentDatabase, LocationDatabase (hotspots), pending_sensor_alerts, pending_citizen_reports, dispatched_incident_ids |
| Percepts | SENSOR_ALERT, CITIZEN_REPORT, RESPONSE_UPDATE |
| Messages sent | INCIDENT_DETECTED, INCIDENT_UPDATE |
| Acquaintances | AssessmentAgent (sends to), EnforcementAgent (receives from) |

---

### AssessmentAgent

| Property | Description |
|---|---|
| Name | AssessmentAgent |
| Responsibilities | Classify each incident by waste type and severity. Apply classification rules to sensor types and citizen report content. Select context-conditioned plans. |
| Goals handled | G2 (Classify incidents), G2.1-G2.3 |
| Plans | assess_incident, handle_update |
| Beliefs maintained | pending_assessments, classified_incidents, classification_rules |
| Percepts | INCIDENT_DETECTED, INCIDENT_UPDATE |
| Messages sent | INCIDENT_CLASSIFIED, DISPATCH_REQUEST |
| Acquaintances | SurveillanceAgent (receives from), EvidenceAgent (sends to), EnforcementAgent (sends to) |

---

### EvidenceAgent

| Property | Description |
|---|---|
| Name | EvidenceAgent |
| Responsibilities | Gather sensor evidence and citizen report evidence for each classified incident. Compile a timestamped evidence package with chain-of-custody record. |
| Goals handled | G3 (Collect and preserve evidence), G3.1-G3.4 |
| Plans | collect_evidence |
| Beliefs maintained | evidence_records, compiled_packages |
| Percepts | INCIDENT_CLASSIFIED |
| Messages sent | EVIDENCE_PACKAGE |
| Acquaintances | AssessmentAgent (receives from), EnforcementAgent (sends to) |

---

### EnforcementAgent

| Property | Description |
|---|---|
| Name | EnforcementAgent |
| Responsibilities | Select and dispatch the appropriate enforcement authority. Attach received evidence packages to case files. Track response status. Escalate overdue cases. |
| Goals handled | G4 (Dispatch authority), G5 (Escalate unresolved), G4.1-G4.3, G5.1-G5.4 |
| Plans | process_dispatch_request, attach_evidence, escalate |
| Beliefs maintained | AuthorityDatabase, pending_dispatches, received_evidence, resolved_incidents, case_files |
| Percepts | DISPATCH_REQUEST, EVIDENCE_PACKAGE |
| Messages sent | RESPONSE_UPDATE |
| Acquaintances | AssessmentAgent (receives from), EvidenceAgent (receives from), SurveillanceAgent (sends to) |

# Phase 5 - Implementation Report
## WasteWatch: Intelligent Illegal Waste Dumping Detection and Enforcement Coordination System

**Student ID:** 11126585
**Course:** DCIT 403 - Intelligent Agent Systems
**Word count:** approximately 680 words

---

## Problem Domain and Justification

Illegal waste dumping is a persistent environmental and public health problem. Enforcement agencies typically learn about dumping only after a citizen complains, often days after the event. Evidence has degraded, offenders have left, and remediation costs are far higher than they would have been with early detection. WasteWatch is designed to close this gap by providing a continuously monitoring, autonomously reasoning agent system that detects incidents from sensor data and citizen reports, classifies them, preserves evidence, and dispatches the correct authority, without requiring a human to watch a screen.

This domain is genuinely agent-appropriate. It is reactive (sensors fire unpredictably), proactive (the system must escalate without being told to), and social (distinct organisational roles such as environmental assessment, forensic evidence management, and enforcement coordination map naturally to distinct agents). A traditional procedural program could not reasonably handle the asynchronous, event-driven nature of the environment without becoming an agent system by another name.

---

## Platform and Language Justification

The implementation uses Python 3 with no external libraries beyond the Python standard library. Python was chosen because:

- The standard library provides all the data structures needed (dataclasses, uuid, time, queue) without introducing dependency complexity.
- Python's class hierarchy supports the abstract base class pattern used for the Agent superclass, which directly mirrors the Prometheus notion of a generic agent with specialised subtypes.
- The language is widely understood and the implementation can be read and evaluated without installing anything beyond Python.

The implementation uses a synchronous, step-based simulation rather than threading. This was a deliberate design choice: threading introduces non-determinism that would obscure the perceive-decide-act cycle in the output. The step-based model makes each agent's cycle explicit and traceable, which better demonstrates the Prometheus design.

---

## Mapping from Prometheus Design to Implementation

The implementation maps directly and consistently to the Phase 1 through Phase 4 design artifacts.

**Agents** in the design correspond to Python classes that extend the abstract `Agent` base class in `src/core/agent.py`. Each agent class is in its own file under `src/agents/`.

**Goals** are implemented as the motivating logic of each agent's plan set. The SurveillanceAgent's goal to detect incidents is expressed in `_plan_handle_sensor_alert` and `_plan_handle_citizen_report`. The EnforcementAgent's goal to escalate unresolved cases is expressed in `check_and_escalate_overdue` and `_plan_escalate`.

**Percepts** are implemented as `Message` objects delivered to each agent's `inbox` list. The `perceive()` method in the base class drains the inbox at the start of each cycle, returning the list of percepts for that step.

**The agent execution cycle** (perceive, decide, act) is implemented in `run_cycle()` in `src/core/agent.py`. Each call to `run_cycle()` calls `perceive()` to collect percepts, `deliberate()` to select plans using `select_plan()`, and `act()` to execute the selected plans. The simulation calls `run_cycle()` for each agent in each step.

**Plan selection** uses the `select_plan()` method, which maps message performatives to plan handler methods. This implements the Prometheus concept of plan selection based on the triggering event. Context-conditioned alternative plan selection occurs inside `_determine_waste_type()` in the AssessmentAgent, where the selected internal sub-procedure depends on which sensor types and keywords are present in the current percept.

**Beliefs** are Python dictionaries stored in the `self.beliefs` dictionary of each agent. Structured data types (Incident, SensorAlert, CitizenReport, Authority, DispatchRecord) are defined as Python dataclasses in the `src/beliefs/` module, mirroring the Prometheus data descriptors.

**Messages** are implemented as the `Message` dataclass in `src/core/message.py`. Each message has a sender, receiver, performative (from the `Performative` enum), and a content dictionary. The `AgentSystem` class acts as the message router.

**Interactions** follow the diagrams in Phase 3 exactly. The SurveillanceAgent always sends first. The AssessmentAgent sends to both EvidenceAgent and EnforcementAgent in parallel. The EvidenceAgent sends to EnforcementAgent. EnforcementAgent closes the loop back to SurveillanceAgent.

---

## Simulation Scenarios

The simulation runs three scenarios across 16 steps.

**Scenario 1** demonstrates a hazardous chemical waste incident triggered by two sensors (chemical and temperature) at an abandoned industrial site. The system classifies it as HAZARDOUS/CRITICAL and dispatches both the EPA and the Hazmat unit. A late citizen report raises confidence from 0.6 to 0.8. After five steps with no authority response, the case is escalated to the Greater Accra Regional Enforcement Unit.

**Scenario 2** demonstrates a non-hazardous waste incident triggered by two citizen reports describing construction debris. The system classifies it as NON_HAZARDOUS/MEDIUM and dispatches the local environmental officer. The case is subsequently escalated when no response is received.

**Scenario 3** demonstrates an air quality incident at a riverbank triggered by two air quality sensors both exceeding the AQI threshold by a factor of three. A citizen report describing river contamination and dead fish corroborates the incident and raises confidence. The case is classified as HAZARDOUS/CRITICAL and escalated after the timeout.

---

## Challenges and Limitations

The primary challenge was designing the plan selection logic for the AssessmentAgent to handle ambiguous inputs without external classification libraries. The implemented solution uses a priority-ordered rule table (sensor types first, keyword analysis second, defaults last) which correctly classifies all three simulation scenarios. A real deployment would benefit from a trained classifier.

A second challenge was implementing escalation in a way that is both deterministic (for simulation readability) and realistic. The step-based timeout (ESCALATION_TIMEOUT_STEPS = 5) achieves this cleanly.

The system has two significant limitations in its current form. First, the sensor network and citizen report system are simulated using a fixed schedule. A real deployment would require interfaces to actual IoT sensor APIs and a web-based citizen portal. Second, the system has no feedback loop for authority response: in the simulation, authorities never actually respond, so all cases eventually escalate. A production system would require a two-way communication channel with field units.

Despite these limitations, the implementation faithfully demonstrates the complete Prometheus pipeline from percept to enforcement action and correctly embodies the intelligent agent properties of reactivity, proactivity, and social ability as defined by Padgham and Winikoff (2004).

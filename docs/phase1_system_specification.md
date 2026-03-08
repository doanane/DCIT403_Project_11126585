# Phase 1 - System Specification
## WasteWatch: Intelligent Illegal Waste Dumping Detection and Enforcement Coordination System

**Student ID:** 11126585
**Course:** DCIT 403 - Intelligent Agent Systems
**Methodology:** Prometheus (Padgham & Winikoff)

---

## 1. Problem Description

### What problem are you solving?

Illegal waste dumping is one of the most persistent and damaging environmental crimes. Across Ghana and across the world, individuals and corporations illegally dispose of hazardous chemicals, construction debris, and household waste at roadsides, riverbeds, and abandoned industrial sites. Current detection methods depend almost entirely on sporadic citizen complaints or infrequent patrol schedules. By the time environmental authorities are notified and arrive at a site, significant damage has already occurred, evidence has degraded or been removed, and the offenders are long gone.

The WasteWatch system addresses this gap by continuously monitoring an environment through an automated sensor network and a citizen reporting portal. When evidence accumulates beyond a threshold, the system autonomously creates an incident record, classifies the waste type and severity, preserves digital evidence, and dispatches the appropriate enforcement authority, all without human intervention in the detection-to-dispatch loop.

### Why is an agent appropriate?

An agent-based approach is appropriate for several reasons drawn directly from Padgham and Winikoff (2004):

- **Reactivity:** The environment changes continuously. Sensors trigger at unexpected times. Citizen reports arrive asynchronously. A reactive agent can respond immediately to each percept as it arrives rather than waiting for a scheduled batch process.

- **Proactivity:** Agents do not simply react. The EnforcementAgent proactively monitors whether dispatched authorities have responded, and if they have not, it escalates the case without waiting for a human to notice the delay.

- **Social ability:** A single monolithic system cannot cleanly separate the concerns of detection, assessment, evidence collection, and enforcement. Multiple agents, each with a specific role, communicate through messages to form a coherent pipeline. This mirrors how real-world environmental response organizations are structured, with distinct departments handling surveillance, forensics, and field response.

- **Situatedness:** Each agent perceives a portion of the real environment (sensor readings, citizen reports, dispatch records) and acts upon it (creating incidents, sending messages, dispatching authorities). The system is embedded in its environment rather than operating in isolation.

### Who are the users and stakeholders?

| Stakeholder | Role |
|---|---|
| Environmental Protection Agency (EPA) | Receives dispatch notifications for hazardous waste incidents |
| National Hazardous Materials Response Unit (HAZMAT) | Responds to critical chemical or radiation-related dumping |
| Accra Metropolitan Environmental Officer | Handles local non-hazardous waste enforcement |
| Greater Accra Regional Enforcement Unit | Acts as escalation authority when primary response is delayed |
| Citizens | Submit reports through the citizen portal |
| System Administrators | Monitor simulation health and incident logs |

---

## 2. Goal Specification

### Top-Level Goals

| Goal ID | Goal Description |
|---|---|
| G1 | Detect illegal waste dumping incidents in monitored areas |
| G2 | Classify each incident by waste type and severity |
| G3 | Collect and preserve tamper-evident digital evidence |
| G4 | Dispatch the correct enforcement authority for each incident |
| G5 | Escalate unresolved incidents to higher authorities |

### Sub-Goals

**G1 - Detect illegal waste dumping incidents:**
- G1.1: Monitor automated sensor network for threshold violations
- G1.2: Receive and validate citizen reports from the citizen portal
- G1.3: Correlate multiple signals from the same location into a single incident
- G1.4: Track confidence levels based on the number of confirming signals
- G1.5: Record known dumping hotspots to flag repeat locations

**G2 - Classify each incident:**
- G2.1: Determine whether the waste is hazardous or non-hazardous
- G2.2: Determine the severity level (low, medium, high, critical)
- G2.3: Use context conditions to select the appropriate classification plan

**G3 - Collect and preserve evidence:**
- G3.1: Record all sensor readings associated with an incident
- G3.2: Record all citizen reports associated with an incident
- G3.3: Record geographic and classification metadata
- G3.4: Compile all items into a numbered evidence package with chain-of-custody record

**G4 - Dispatch enforcement authority:**
- G4.1: Select authority based on waste type and severity
- G4.2: Notify the selected authority with location and evidence reference
- G4.3: Confirm dispatch status to the SurveillanceAgent

**G5 - Escalate unresolved incidents:**
- G5.1: Track elapsed simulation steps since dispatch
- G5.2: Detect when no response has been received within the timeout window
- G5.3: Alert the regional enforcement unit
- G5.4: Update case status to escalated

---

## 3. Functionalities

The following functionalities describe what the system must do without specifying implementation mechanisms.

| ID | Functionality |
|---|---|
| F1 | Monitor sensor network and receive alerts when readings exceed safe thresholds |
| F2 | Receive and store citizen waste dumping reports |
| F3 | Correlate multiple sensor alerts from the same location |
| F4 | Correlate citizen reports from the same location |
| F5 | Create a unified incident record when detection threshold is reached |
| F6 | Track confidence levels for each incident |
| F7 | Identify known dumping hotspots |
| F8 | Classify waste type using sensor types and citizen report keyword analysis |
| F9 | Determine incident severity based on sensor readings relative to thresholds |
| F10 | Apply context-conditioned plan selection for alternative classification paths |
| F11 | Collect all available evidence for a classified incident |
| F12 | Compile an evidence package with a chain-of-custody record |
| F13 | Select the appropriate enforcement authority based on classification |
| F14 | Dispatch the selected authority with incident details |
| F15 | Track dispatch status for each incident |
| F16 | Detect overdue responses using a step-based timeout |
| F17 | Escalate overdue incidents to the regional enforcement unit |
| F18 | Update incident status throughout the pipeline |
| F19 | Produce a final incident report summarising all cases |

---

## 4. Scenarios

### Scenario 1: Chemical Hazardous Waste at Abandoned Industrial Site

A sensor at an abandoned industrial site on the Tema Port Road detects elevated toluene levels (157 ppm against a threshold of 50 ppm). In the next simulation step, a temperature sensor at the same location detects 134 degrees C (threshold 45 degrees C), consistent with an exothermic chemical reaction. The SurveillanceAgent accumulates two sensor confirmations, meets the detection threshold, and creates incident INC-A.

The AssessmentAgent receives the INCIDENT_DETECTED message. It reads the sensor types (chemical, temperature) and their values and selects the plan for hazardous assessment. It classifies the waste as HAZARDOUS with severity CRITICAL because the chemical reading is three times the threshold and the temperature reading exceeds 120 degrees C.

The EvidenceAgent receives INCIDENT_CLASSIFIED and compiles an evidence package containing both sensor readings, the geographic location record, and the assessment metadata.

The EnforcementAgent receives the DISPATCH_REQUEST and the EVIDENCE_PACKAGE. It selects both the Ghana EPA and the National Hazardous Materials Response Unit based on the HAZARDOUS/CRITICAL classification. It dispatches both authorities and notifies the SurveillanceAgent.

In the next step, a citizen submits a report describing trucks unloading metal drums at night with a strong chemical smell. The SurveillanceAgent correlates this with the existing incident, raising confidence from 0.6 to 0.8.

After five simulation steps with no response received, the EnforcementAgent detects the overdue status and escalates the case to the Greater Accra Regional Enforcement Unit.

---

### Scenario 2: Non-Hazardous Construction Waste at Roadside

A citizen report describes a large pile of construction rubble and broken concrete at a roadside clearing on the Accra-Kumasi Highway. The SurveillanceAgent stores the report but waits for a second confirmation. One step later, a second citizen confirms the same location, adding that mattresses and garbage bags were added overnight.

The SurveillanceAgent reaches the citizen report threshold, creates incident INC-B, and sends INCIDENT_DETECTED to the AssessmentAgent.

The AssessmentAgent reads the citizen report descriptions. It finds no chemical or radiation sensor types. It performs keyword analysis on the report texts and finds high-scoring solid waste keywords (rubble, concrete, construction, debris). It selects the non-hazardous assessment plan and classifies the waste as NON_HAZARDOUS with severity MEDIUM because there are two confirming reports but no sensor data.

The EvidenceAgent collects both citizen reports (one with a photo) and compiles the evidence package. The EnforcementAgent selects the Accra Metropolitan Environmental Officer as the appropriate local authority for a non-hazardous medium-severity case. The case is dispatched and later escalated when no response is received.

---

### Scenario 3: Air Quality Degradation at Riverbank

Two air quality sensors at the Densu River South Bank both exceed the AQI threshold of 100, reporting 310 and 290 respectively. The SurveillanceAgent detects the double confirmation and creates incident INC-C.

The AssessmentAgent identifies the air_quality sensor type as hazardous by its classification rules. The readings are 3.1 and 2.9 times the threshold, placing severity at CRITICAL. The incident is classified as HAZARDOUS/CRITICAL.

The EvidenceAgent compiles the two sensor readings. Shortly after, a citizen report arrives describing foul-smelling liquid entering the river and dead fish near the bank, further corroborating the incident. The SurveillanceAgent correlates this report with INC-C, raising confidence from 0.6 to 0.8.

After five steps with no authority response, the EnforcementAgent escalates to the Regional Enforcement Unit. This scenario demonstrates the system's ability to handle environmental contamination at a water source, which carries additional ecological urgency.

---

### Scenario 4: Single Sensor Alert (Insufficient Evidence)

A single chemical sensor fires at a location. The SurveillanceAgent stores the alert but no second sensor confirmation arrives and no citizen report is filed. The SurveillanceAgent notes the pending alert but does not create an incident. No messages are sent to downstream agents. The system waits for additional confirming evidence, demonstrating conservative behaviour to avoid false positive dispatches.

---

### Scenario 5: Late-Arriving Citizen Report Corroborating Active Incident

An incident has already been created based on sensor data and dispatched to authorities. A citizen report arrives later describing activity consistent with the already-detected incident. The SurveillanceAgent recognises the location as matching an active incident and correlates the new report directly with it, updating the confidence score. The updated confidence is forwarded to the AssessmentAgent via INCIDENT_UPDATE so the assessment record remains accurate.

---

## 5. Environment Description

### What environment does the agent operate in?

The WasteWatch system is situated in a monitored geographic environment consisting of designated surveillance zones. Each zone has:

- A fixed sensor network with sensors of different types (chemical, temperature, air quality, radiation)
- Public access to the citizen reporting portal
- Known authority jurisdictions and contact channels

The environment is:
- **Partially observable:** Agents perceive only what sensors and citizens report. Unknown dumping sites generate no percepts.
- **Non-deterministic:** The timing and content of sensor alerts and citizen reports cannot be predicted.
- **Dynamic:** The environment changes over time. Sensor readings change. More waste may be added to a site. Authorities may or may not respond.
- **Discrete and event-driven:** The simulation advances in steps, with events arriving at scheduled steps.

### What does the agent perceive?

| Percept | Description | Received by |
|---|---|---|
| SENSOR_ALERT | A structured message from a sensor containing type, value, unit, threshold, and location | SurveillanceAgent |
| CITIZEN_REPORT | A structured message from the citizen portal containing location, description, photo flag | SurveillanceAgent |
| INCIDENT_DETECTED | A message from SurveillanceAgent describing a newly confirmed incident | AssessmentAgent |
| INCIDENT_UPDATE | A message from SurveillanceAgent with updated confidence for a known incident | AssessmentAgent |
| INCIDENT_CLASSIFIED | A message from AssessmentAgent with waste type and severity | EvidenceAgent |
| DISPATCH_REQUEST | A message from AssessmentAgent requesting authority dispatch | EnforcementAgent |
| EVIDENCE_PACKAGE | A message from EvidenceAgent containing compiled evidence | EnforcementAgent |
| RESPONSE_UPDATE | A message from EnforcementAgent to SurveillanceAgent with dispatch confirmation | SurveillanceAgent |

### What can the agent act upon?

| Action | Agent | Description |
|---|---|---|
| Create incident record | SurveillanceAgent | Creates Incident object in IncidentDatabase |
| Update incident record | SurveillanceAgent | Adds correlated reports or updates status |
| Send INCIDENT_DETECTED | SurveillanceAgent | Sends message to AssessmentAgent |
| Send INCIDENT_UPDATE | SurveillanceAgent | Sends confidence update to AssessmentAgent |
| Classify incident | AssessmentAgent | Updates classified_incidents belief |
| Send INCIDENT_CLASSIFIED | AssessmentAgent | Sends classification to EvidenceAgent |
| Send DISPATCH_REQUEST | AssessmentAgent | Sends dispatch order to EnforcementAgent |
| Collect evidence | EvidenceAgent | Gathers sensor and report evidence items |
| Compile evidence package | EvidenceAgent | Creates timestamped, numbered package |
| Send EVIDENCE_PACKAGE | EvidenceAgent | Sends package to EnforcementAgent |
| Select authority | EnforcementAgent | Queries AuthorityDatabase for matching authority |
| Dispatch authority | EnforcementAgent | Records dispatch and prints dispatch action |
| Send RESPONSE_UPDATE | EnforcementAgent | Confirms dispatch status to SurveillanceAgent |
| Escalate incident | EnforcementAgent | Dispatches regional authority when overdue |

# Phase 4 - Detailed Design
## WasteWatch: Intelligent Illegal Waste Dumping Detection and Enforcement Coordination System

---

## 1. Capabilities

Capabilities group related behaviors within an agent. Each capability has a trigger (what activates it) and a set of plans it can execute.

### SurveillanceAgent Capabilities

#### Capability: SensorMonitoring
- **Trigger:** Incoming SENSOR_ALERT message
- **Related plans:** handle_sensor_alert, create_or_update_incident_from_sensors
- **Behaviors:** Accumulates sensor alerts by location. When alert count reaches SENSOR_CONFIRMATION_THRESHOLD (2), creates or updates an incident. Tracks which sensor types have confirmed.

#### Capability: ReportProcessing
- **Trigger:** Incoming CITIZEN_REPORT message
- **Related plans:** handle_citizen_report, create_incident_from_reports
- **Behaviors:** Accumulates citizen reports by location. When report count reaches CITIZEN_REPORT_THRESHOLD (2), creates an incident. If an incident already exists at the location, correlates the report with it and updates confidence.

#### Capability: IncidentManagement
- **Trigger:** Detection threshold crossed, or incoming RESPONSE_UPDATE
- **Related plans:** dispatch_to_assessment, notify_assessment_update, handle_response_update
- **Behaviors:** Creates Incident objects in IncidentDatabase. Sends INCIDENT_DETECTED and INCIDENT_UPDATE messages. Updates incident status when RESPONSE_UPDATE is received.

---

### AssessmentAgent Capabilities

#### Capability: WasteTypeClassification
- **Trigger:** INCIDENT_DETECTED message received
- **Related plans:** assess_incident (parent plan)
- **Behaviors:** Determines waste type by checking sensor types against classification rules and performing keyword analysis on citizen report descriptions.

#### Capability: SeverityDetermination
- **Trigger:** Internal, called within assess_incident
- **Related plans:** determine_severity (sub-plan of assess_incident)
- **Behaviors:** Evaluates sensor reading values against thresholds. Assigns severity score 0-4. Maps score to severity label.

#### Capability: UpdateProcessing
- **Trigger:** INCIDENT_UPDATE message received
- **Related plans:** handle_update
- **Behaviors:** Updates confidence in the classified_incidents belief record.

---

### EvidenceAgent Capabilities

#### Capability: EvidenceCollection
- **Trigger:** INCIDENT_CLASSIFIED message received
- **Related plans:** collect_evidence
- **Behaviors:** Gathers sensor readings, citizen reports, geographic metadata, and assessment metadata. Stores all items in evidence_records.

#### Capability: PackageCompilation
- **Trigger:** Internal, called within collect_evidence
- **Related plans:** compile_package (sub-plan of collect_evidence)
- **Behaviors:** Creates an EVIDENCE_PACKAGE with a unique ID, item count, compiled timestamp, and chain-of-custody record. Sends the package to EnforcementAgent.

---

### EnforcementAgent Capabilities

#### Capability: AuthorityDispatch
- **Trigger:** DISPATCH_REQUEST message received
- **Related plans:** process_dispatch_request
- **Behaviors:** Queries AuthorityDatabase to select appropriate authorities. Records dispatch. Confirms to SurveillanceAgent.

#### Capability: EvidenceAttachment
- **Trigger:** EVIDENCE_PACKAGE message received
- **Related plans:** attach_evidence
- **Behaviors:** Links evidence package to case file. Prints case summary.

#### Capability: EscalationMonitoring
- **Trigger:** Per-step check, no external message trigger
- **Related plans:** check_and_escalate_overdue, escalate
- **Behaviors:** Tracks steps elapsed since dispatch for each active case. When threshold exceeded and evidence is attached, initiates escalation plan.

---

## 2. Plans

### SurveillanceAgent Plans

#### Plan: handle_sensor_alert
- **Trigger:** SENSOR_ALERT message
- **Context condition:** None (always applicable when SENSOR_ALERT received)
- **Steps:**
  1. Extract SensorAlert data from message content
  2. Append to pending_sensor_alerts[location_key]
  3. If count >= SENSOR_CONFIRMATION_THRESHOLD: execute _create_or_update_incident_from_sensors
  4. Else: print count status, wait

#### Plan: handle_citizen_report
- **Trigger:** CITIZEN_REPORT message
- **Context condition:** None
- **Steps:**
  1. Extract CitizenReport data from message content
  2. If incident already exists at location_key: correlate report, call _notify_assessment_update
  3. Else: append to pending_citizen_reports[location_key]
  4. If report count >= CITIZEN_REPORT_THRESHOLD: execute _create_incident_from_reports

#### Plan: handle_response_update (Alternative Plan)
- **Trigger:** RESPONSE_UPDATE message
- **Context condition:** message.performative == RESPONSE_UPDATE
- **Steps:**
  1. Extract incident_id and status from content
  2. Update incident status in IncidentDatabase

---

### AssessmentAgent Plans

#### Plan: assess_incident
- **Trigger:** INCIDENT_DETECTED message
- **Context condition:** None (always applicable for INCIDENT_DETECTED)
- **Steps:**
  1. Store content in pending_assessments belief
  2. Call _determine_waste_type (applies classification rules and keyword analysis)
  3. Call _determine_severity (applies threshold comparison)
  4. Store result in classified_incidents belief
  5. Send INCIDENT_CLASSIFIED to EvidenceAgent
  6. Send DISPATCH_REQUEST to EnforcementAgent

**Alternative plan selection within _determine_waste_type:**

| Condition | Selected Sub-Plan | Outcome |
|---|---|---|
| sensor_types contains "chemical" or "radiation" or "air_quality" | Hazardous rule match | waste_type = hazardous |
| No hazardous sensor types, report keywords match solid waste | Solid waste keyword match | waste_type = non_hazardous |
| No hazardous sensor types, report keywords match chemical | Chemical keyword match | waste_type = hazardous |
| No matching sensor types or keywords | Default | waste_type = non_hazardous |

#### Plan: handle_update
- **Trigger:** INCIDENT_UPDATE message
- **Context condition:** incident_id exists in classified_incidents
- **Steps:**
  1. Extract incident_id and new confidence
  2. Update classified_incidents[incident_id]["confidence"]

---

### EvidenceAgent Plans

#### Plan: collect_evidence
- **Trigger:** INCIDENT_CLASSIFIED message
- **Context condition:** None
- **Steps:**
  1. Call _gather_sensor_evidence: creates one evidence item per sensor alert
  2. Call _gather_report_evidence: creates one evidence item per citizen report (flags photo if available)
  3. Call _gather_metadata_evidence: creates geo_location and detection_metadata items
  4. Store all items in evidence_records[incident_id]
  5. Generate unique package_id
  6. Create evidence package dict with chain_of_custody entry
  7. Store in compiled_packages[incident_id]
  8. Send EVIDENCE_PACKAGE to EnforcementAgent

---

### EnforcementAgent Plans

#### Plan: process_dispatch_request
- **Trigger:** DISPATCH_REQUEST message
- **Context condition:** None
- **Steps:**
  1. Store dispatch info in pending_dispatches with dispatch_step=0
  2. Query authority_db.select_authority(waste_type, severity)
  3. For each selected authority: create DispatchRecord, record it
  4. Print dispatch notification for each authority
  5. Create case_file entry
  6. Send RESPONSE_UPDATE to SurveillanceAgent

**Alternative plan selection within select_authority:**

| Condition | Selected Authorities |
|---|---|
| waste_type == hazardous AND severity == critical | EPA + HAZMAT |
| waste_type == hazardous | EPA only |
| waste_type == non_hazardous AND severity == high | EPA only |
| waste_type == non_hazardous | LOCAL_ENV |
| unknown | EPA |

#### Plan: attach_evidence
- **Trigger:** EVIDENCE_PACKAGE message
- **Context condition:** None
- **Steps:**
  1. Store package in received_evidence[incident_id]
  2. Link package_id to case_file[incident_id]
  3. Update case status to evidence_attached
  4. Print case summary

#### Plan: escalate
- **Trigger:** Called internally by check_and_escalate_overdue, or ESCALATION_ALERT message
- **Context condition:** incident has evidence_attached status and has not been escalated
- **Steps:**
  1. Get REGIONAL authority from AuthorityDatabase
  2. Create DispatchRecord for REGIONAL authority
  3. Record dispatch
  4. Update case status to escalated
  5. Add REGIONAL to case authorities list
  6. Print escalation notification

---

## 3. Data Description

### Beliefs / Knowledge Structures

#### SurveillanceAgent

| Belief | Type | Description |
|---|---|---|
| incidents | IncidentDatabase | All created Incident objects, keyed by incident_id |
| locations | LocationDatabase | Location records and hotspot tracking |
| pending_sensor_alerts | dict[str, list[SensorAlert]] | Accumulated sensor alerts per location_key |
| pending_citizen_reports | dict[str, list[CitizenReport]] | Accumulated citizen reports per location_key |
| dispatched_incident_ids | set[str] | IDs of incidents already sent to AssessmentAgent |

#### AssessmentAgent

| Belief | Type | Description |
|---|---|---|
| pending_assessments | dict[str, dict] | Raw incident content awaiting or under assessment |
| classified_incidents | dict[str, dict] | Classification results keyed by incident_id |
| classification_rules | dict[str, str] | Maps sensor_type to initial waste_type determination |

#### EvidenceAgent

| Belief | Type | Description |
|---|---|---|
| evidence_records | dict[str, list[dict]] | All evidence items per incident_id |
| compiled_packages | dict[str, dict] | Complete evidence packages per incident_id |

#### EnforcementAgent

| Belief | Type | Description |
|---|---|---|
| authority_db | AuthorityDatabase | Static authority contact records and dispatch policy |
| pending_dispatches | dict[str, dict] | Active dispatch records with dispatch_step tracking |
| received_evidence | dict[str, dict] | Evidence packages received from EvidenceAgent |
| resolved_incidents | set[str] | Incidents that have been escalated or resolved |
| case_files | dict[str, dict] | Complete case record combining dispatch and evidence |

---

### Key Data Structures

#### Incident Object

| Field | Type | Description |
|---|---|---|
| incident_id | str | Unique identifier (INC-XXXX format) |
| location_key | str | Zone identifier |
| location_description | str | Human-readable location |
| detected_at | float | Unix timestamp of creation |
| sensor_alerts | list[SensorAlert] | All triggering sensor alerts |
| citizen_reports | list[CitizenReport] | All correlated citizen reports |
| waste_type | str or None | Set by AssessmentAgent |
| severity | str or None | Set by AssessmentAgent |
| status | str | detected, classified, dispatched, escalated, resolved |
| confidence_level() | method | Returns float based on signal count |

#### Evidence Package

| Field | Type | Description |
|---|---|---|
| package_id | str | Unique identifier (EP-XXXX format) |
| incident_id | str | Associated incident |
| evidence_items | list[dict] | Each item has type, description, source, timestamp |
| chain_of_custody | list[dict] | Custodian, action, timestamp sequence |
| compiled_at | float | Compilation timestamp |
| item_count | int | Total items |

---

## 4. Percepts and Actions

### All Percepts

| Percept | Type | Agent | Trigger |
|---|---|---|---|
| SENSOR_ALERT | Message | SurveillanceAgent | Sensor reading exceeds threshold |
| CITIZEN_REPORT | Message | SurveillanceAgent | Citizen submits report via portal |
| RESPONSE_UPDATE | Message | SurveillanceAgent | EnforcementAgent confirms dispatch |
| INCIDENT_DETECTED | Message | AssessmentAgent | SurveillanceAgent creates incident |
| INCIDENT_UPDATE | Message | AssessmentAgent | New signal corroborates existing incident |
| INCIDENT_CLASSIFIED | Message | EvidenceAgent | AssessmentAgent completes classification |
| DISPATCH_REQUEST | Message | EnforcementAgent | AssessmentAgent issues dispatch order |
| EVIDENCE_PACKAGE | Message | EnforcementAgent | EvidenceAgent completes package |

### All Actions

| Action | Agent | Description |
|---|---|---|
| Store sensor alert | SurveillanceAgent | Appends SensorAlert to pending_sensor_alerts[loc] |
| Store citizen report | SurveillanceAgent | Appends CitizenReport to pending_citizen_reports[loc] |
| Create incident | SurveillanceAgent | Creates Incident in IncidentDatabase |
| Correlate report to incident | SurveillanceAgent | Appends report to existing Incident object |
| Update incident status | SurveillanceAgent | Changes status field in IncidentDatabase |
| Send INCIDENT_DETECTED | SurveillanceAgent | Delivers message to AssessmentAgent inbox |
| Send INCIDENT_UPDATE | SurveillanceAgent | Delivers update message to AssessmentAgent inbox |
| Record hotspot | SurveillanceAgent | Increments HotspotRecord in LocationDatabase |
| Classify waste type | AssessmentAgent | Updates classified_incidents belief |
| Determine severity | AssessmentAgent | Computes severity score and maps to label |
| Send INCIDENT_CLASSIFIED | AssessmentAgent | Delivers message to EvidenceAgent inbox |
| Send DISPATCH_REQUEST | AssessmentAgent | Delivers message to EnforcementAgent inbox |
| Gather sensor evidence | EvidenceAgent | Creates evidence item per sensor alert |
| Gather report evidence | EvidenceAgent | Creates evidence item per citizen report |
| Gather metadata evidence | EvidenceAgent | Creates geo_location and classification items |
| Compile evidence package | EvidenceAgent | Builds package with package_id and chain of custody |
| Send EVIDENCE_PACKAGE | EvidenceAgent | Delivers package to EnforcementAgent inbox |
| Select authority | EnforcementAgent | Queries authority policy table |
| Dispatch authority | EnforcementAgent | Records DispatchRecord and prints dispatch notice |
| Create case file | EnforcementAgent | Initialises case_files entry |
| Attach evidence to case | EnforcementAgent | Links package_id to case_files entry |
| Send RESPONSE_UPDATE | EnforcementAgent | Delivers status update to SurveillanceAgent inbox |
| Escalate incident | EnforcementAgent | Dispatches REGIONAL authority, updates case status |

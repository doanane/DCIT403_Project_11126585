# Phase 3 - Interaction Design
## WasteWatch: Intelligent Illegal Waste Dumping Detection and Enforcement Coordination System

---

## 1. Interaction Diagrams

### Interaction Diagram 1 - Scenario 1: Chemical Hazardous Waste (Sensor-Triggered)

```
SensorNetwork   SurveillanceAgent   AssessmentAgent   EvidenceAgent   EnforcementAgent
     |                 |                   |                |                |
     | SENSOR_ALERT    |                   |                |                |
     | (chemical,      |                   |                |                |
     |  SA-001)        |                   |                |                |
     |---------------->|                   |                |                |
     |                 | [stores alert,     |                |                |
     |                 |  count=1, wait]    |                |                |
     |                 |                   |                |                |
     | SENSOR_ALERT    |                   |                |                |
     | (temperature,   |                   |                |                |
     |  SA-002)        |                   |                |                |
     |---------------->|                   |                |                |
     |                 | [count=2, creates  |                |                |
     |                 |  INC-A]            |                |                |
     |                 | INCIDENT_DETECTED  |                |                |
     |                 | (INC-A, LOC-A,     |                |                |
     |                 |  sensors=[chem,    |                |                |
     |                 |  temp],            |                |                |
     |                 |  confidence=0.6)   |                |                |
     |                 |------------------>|                |                |
     |                 |                   | [selects plan: |                |
     |                 |                   |  assess_hazard]|                |
     |                 |                   | INCIDENT_CLASSIFIED            |
     |                 |                   | (INC-A,        |                |
     |                 |                   |  HAZARDOUS,    |                |
     |                 |                   |  CRITICAL)     |                |
     |                 |                   |--------------->|                |
     |                 |                   |                | [collects     |
     |                 |                   |                |  evidence]    |
     |                 |                   | DISPATCH_REQUEST               |
     |                 |                   | (INC-A,        |                |
     |                 |                   |  HAZARDOUS,    |                |
     |                 |                   |  CRITICAL)     |                |
     |                 |                   |----------------|--------------->|
     |                 |                   |                | EVIDENCE_PACKAGE
     |                 |                   |                | (EP-001, INC-A)
     |                 |                   |                |--------------->|
     |                 |                   |                |                | [dispatches
     |                 |                   |                |                |  EPA + HAZMAT]
     |                 | RESPONSE_UPDATE    |                |                |
     |                 | (INC-A,            |                |                |
     |                 |  dispatched)       |                |                |
     |                 |<--------------------------------------------------|
     |                 |                   |                |                |
     | [Step +5]       |                   |                |                |
     |                 |                   |                |                |
     |                 |                   |                |                | [timeout detected]
     |                 |                   |                |                | [escalates to
     |                 |                   |                |                |  REGIONAL]
```

---

### Interaction Diagram 2 - Scenario 2: Non-Hazardous Waste (Report-Triggered)

```
CitizenPortal   SurveillanceAgent   AssessmentAgent   EvidenceAgent   EnforcementAgent
     |                 |                   |                |                |
     | CITIZEN_REPORT  |                   |                |                |
     | (CR-002, LOC-B, |                   |                |                |
     |  construction   |                   |                |                |
     |  rubble)        |                   |                |                |
     |---------------->|                   |                |                |
     |                 | [stores report,    |                |                |
     |                 |  count=1, wait]    |                |                |
     |                 |                   |                |                |
     | CITIZEN_REPORT  |                   |                |                |
     | (CR-003, LOC-B, |                   |                |                |
     |  confirming)    |                   |                |                |
     |---------------->|                   |                |                |
     |                 | [count=2, creates  |                |                |
     |                 |  INC-B]            |                |                |
     |                 | INCIDENT_DETECTED  |                |                |
     |                 | (INC-B, LOC-B,     |                |                |
     |                 |  reports=2,        |                |                |
     |                 |  confidence=0.4)   |                |                |
     |                 |------------------>|                |                |
     |                 |                   | [selects plan: |                |
     |                 |                   |  assess_solid] |                |
     |                 |                   | INCIDENT_CLASSIFIED            |
     |                 |                   | (INC-B,        |                |
     |                 |                   |  NON_HAZARDOUS,|                |
     |                 |                   |  MEDIUM)       |                |
     |                 |                   |--------------->|                |
     |                 |                   |                | [collects 2   |
     |                 |                   |                |  reports]     |
     |                 |                   | DISPATCH_REQUEST               |
     |                 |                   | (INC-B,        |                |
     |                 |                   |  NON_HAZARDOUS)|                |
     |                 |                   |----------------|--------------->|
     |                 |                   |                | EVIDENCE_PACKAGE
     |                 |                   |                | (EP-002, INC-B)
     |                 |                   |                |--------------->|
     |                 |                   |                |                | [dispatches
     |                 |                   |                |                |  LOCAL_ENV]
     |                 | RESPONSE_UPDATE    |                |                |
     |                 | (INC-B,            |                |                |
     |                 |  dispatched)       |                |                |
     |                 |<--------------------------------------------------|
```

---

### Interaction Diagram 3 - Scenario 5: Late Citizen Report Corroborates Active Incident

```
CitizenPortal   SurveillanceAgent   AssessmentAgent
     |                 |                   |
     |                 | [INC-C already    |
     |                 |  exists, is in    |
     |                 |  dispatched state]|
     |                 |                   |
     | CITIZEN_REPORT  |                   |
     | (CR-004, LOC-C, |                   |
     |  river          |                   |
     |  contamination) |                   |
     |---------------->|                   |
     |                 | [location match   |
     |                 |  found: INC-C]    |
     |                 | [appends report   |
     |                 |  to INC-C]        |
     |                 | [confidence       |
     |                 |  0.6 -> 0.8]      |
     |                 | INCIDENT_UPDATE   |
     |                 | (INC-C,           |
     |                 |  confidence=0.8)  |
     |                 |------------------>|
     |                 |                   | [updates belief
     |                 |                   |  record]
```

---

## 2. Message Descriptors

### SENSOR_ALERT

| Field | Type | Description |
|---|---|---|
| alert_id | string | Unique alert identifier (e.g., SA-001) |
| sensor_id | string | Sensor hardware identifier |
| sensor_type | string | One of: chemical, temperature, air_quality, radiation, visual |
| location_key | string | Zone identifier (e.g., LOC-A) |
| location_description | string | Human-readable location name |
| reading_value | float | The measured value |
| unit | string | Unit of measurement (ppm, degrees_C, AQI) |
| threshold | float | Safe threshold value in same unit |
| timestamp | float | Unix timestamp of reading |

**Sender:** SensorNetwork (environment)
**Receiver:** SurveillanceAgent

---

### CITIZEN_REPORT

| Field | Type | Description |
|---|---|---|
| report_id | string | Unique report identifier (e.g., CR-001) |
| location_key | string | Zone identifier |
| location_description | string | Human-readable location name |
| description | string | Free-text description from citizen |
| photo_available | boolean | Whether a photo was submitted |
| timestamp | float | Unix timestamp of report submission |

**Sender:** CitizenPortal (environment)
**Receiver:** SurveillanceAgent

---

### INCIDENT_DETECTED

| Field | Type | Description |
|---|---|---|
| incident_id | string | Unique incident identifier (e.g., INC-DD8F) |
| location_key | string | Zone identifier |
| location_description | string | Human-readable location name |
| sensor_types | list[string] | Types of sensors that triggered |
| sensor_alerts | list[dict] | Full sensor reading details |
| citizen_reports | list[dict] | Summary of citizen reports |
| confidence | float | Calculated confidence level (0.0-1.0) |
| detected_at | float | Unix timestamp of incident creation |

**Sender:** SurveillanceAgent
**Receiver:** AssessmentAgent

---

### INCIDENT_CLASSIFIED

| Field | Type | Description |
|---|---|---|
| incident_id | string | Incident identifier |
| location_key | string | Zone identifier |
| location_description | string | Human-readable location name |
| waste_type | string | One of: hazardous, non_hazardous, unknown_requires_investigation |
| severity | string | One of: low, medium, high, critical |
| confidence | float | Confidence from SurveillanceAgent |
| sensor_alerts | list[dict] | Forwarded sensor data |
| citizen_reports | list[dict] | Forwarded report data |

**Sender:** AssessmentAgent
**Receivers:** EvidenceAgent, EnforcementAgent

---

### DISPATCH_REQUEST

Same structure as INCIDENT_CLASSIFIED. Sent in parallel with INCIDENT_CLASSIFIED.

**Sender:** AssessmentAgent
**Receiver:** EnforcementAgent

---

### EVIDENCE_PACKAGE

| Field | Type | Description |
|---|---|---|
| package_id | string | Unique package identifier (e.g., EP-DDC6) |
| incident_id | string | Associated incident identifier |
| location_key | string | Zone identifier |
| location_description | string | Human-readable location name |
| waste_type | string | From assessment |
| severity | string | From assessment |
| confidence | float | From assessment |
| evidence_items | list[dict] | All evidence items with type, description, source, timestamp |
| compiled_at | float | Unix timestamp of package compilation |
| item_count | int | Total number of evidence items |
| chain_of_custody | list[dict] | Custodian, action, timestamp records |

**Sender:** EvidenceAgent
**Receiver:** EnforcementAgent

---

### RESPONSE_UPDATE

| Field | Type | Description |
|---|---|---|
| incident_id | string | Incident being updated |
| status | string | New status (e.g., dispatched, escalated) |

**Sender:** EnforcementAgent
**Receiver:** SurveillanceAgent

---

### INCIDENT_UPDATE

| Field | Type | Description |
|---|---|---|
| incident_id | string | Incident being updated |
| additional_reports | int | Number of citizen reports now attached |
| confidence | float | Updated confidence value |

**Sender:** SurveillanceAgent
**Receiver:** AssessmentAgent

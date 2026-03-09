# Phase 3 - Interaction Design
## MedStock: Hospital Pharmacy Stock Depletion and Emergency Resupply Coordination

**Student ID:** 11126585
**Course:** DCIT 403 - Intelligent Agent Systems
**Methodology:** Prometheus (Padgham and Winikoff, 2004)

---

## 1. Message Performatives

All inter-agent communication uses the Message dataclass with the following performatives defined in the Performative enum:

| Performative | Direction | Purpose |
|---|---|---|
| STOCK_READING | PharmacySensor -> StockMonitorAgent | Delivers a stock level reading for a specific drug in a specific ward |
| STOCK_ALERT | StockMonitorAgent -> SupplyAssessmentAgent | Notifies of a detected shortage above the alerting threshold |
| SHORTAGE_CLASSIFIED | SupplyAssessmentAgent -> TransferCoordinationAgent or ProcurementEscalationAgent | Delivers a fully classified shortage record with routing-specific flags |
| TRANSFER_RESULT | TransferCoordinationAgent -> ProcurementEscalationAgent | Reports the outcome (success or failure) of a transfer attempt |
| PROCUREMENT_REQUEST | Internal (used in procurement record) | Represents a procurement order in the supplier database |
| ESCALATION_NOTICE | Internal | Represents escalation status in procurement record |
| STATUS_UPDATE | Reserved | Future use for status broadcasting |

### Message Structure

Each message carries a content dictionary. The key fields per performative are:

**STOCK_READING content:**
- drug_id: str
- ward_id: str
- quantity: float
- step: int

**STOCK_ALERT content:**
- drug_id, ward_id, current_stock, reorder_threshold, severity (str), quantity_needed, step

**SHORTAGE_CLASSIFIED content:**
- shortage_id, drug_id, drug_name, ward_id, severity, category, current_stock, reorder_threshold, quantity_needed, step
- await_transfer_result (bool, only present when sent to ProcurementEscalationAgent for CRITICAL cases)

**TRANSFER_RESULT content:**
- shortage_id, drug_id, drug_name, ward_id, success (bool), reason (str), severity, category, quantity_needed, step
- transfer_id, transfer_qty, from_ward (only on success)

---

## 2. Interaction Diagrams

### Scenario 1: Insulin ICU - Transfer Success

```
Step 1
PharmacySensor          StockMonitorAgent     SupplyAssessmentAgent
    |                         |                       |
    |-- STOCK_READING ------->|                       |
    |   (insulin, ICU, 8)     |                       |
    |                         |-- STOCK_ALERT ------->|
    |                         |   (CRITICAL, need=92) |
    |                         |                       |
                                                      |
                        TransferCoordinationAgent     |
                                |                     |
                                |<-- SHORTAGE_CLASSIFIED (CRITICAL, ESSENTIAL)
                                |
                                |  [Search wards: EMERGENCY has 120 units, ratio=1.2 > 0.5]
                                |  [Transfer 60 units EMERGENCY -> ICU]
                                |
                     ProcurementEscalationAgent
                                |
                                |<-- SHORTAGE_CLASSIFIED (await_transfer_result=True)
                                |   [Waiting for transfer outcome]
                                |
                                |<-- TRANSFER_RESULT (success=True, TR-001)
                                |
                                |  [Mark insulin_ICU as RESOLVED]
                                |  [No procurement initiated]

Outcome: TR-001 COMPLETED, no procurement created
```

### Scenario 2: Morphine SURGICAL - Controlled Substance, Escalation

```
Step 3
PharmacySensor          StockMonitorAgent     SupplyAssessmentAgent
    |                         |                       |
    |-- STOCK_READING ------->|                       |
    |   (morphine, SURGICAL,7)|                       |
    |                         |-- STOCK_ALERT ------->|
    |                         |   (HIGH, need=43)     |
    |                         |                       |
                                          TransferCoordinationAgent
                                                      |
                                        <-- SHORTAGE_CLASSIFIED (HIGH, CONTROLLED)
                                                      |
                                          [CONTROLLED policy: transfer denied]
                                                      |
                               ProcurementEscalationAgent
                                                      |
                               <-- TRANSFER_RESULT (success=False, controlled_substance_policy)
                                                      |
                                  [find_supplier("controlled") -> PharmaControl Ltd]
                                  [create PR-001, dispatch_step=3]

Steps 4-7: No events. Each cycle:
  ProcurementEscalationAgent._plan_check_and_escalate()
  -> current_step - dispatch_step < 5, no escalation yet

Step 8:
  ProcurementEscalationAgent._plan_check_and_escalate()
  -> current_step(8) - dispatch_step(3) = 5 >= ESCALATION_TIMEOUT_STEPS
  -> PR-001 status = ESCALATED, escalated_step = 8

Outcome: TR-002 FAILED (controlled policy), PR-001 ESCALATED at step 8
```

### Scenario 3a: Amoxicillin SURGICAL - Transfer Success

```
Step 8
PharmacySensor          StockMonitorAgent     SupplyAssessmentAgent
    |                         |                       |
    |-- STOCK_READING ------->|                       |
    |   (amoxicillin,         |                       |
    |    SURGICAL, 40)        |-- STOCK_ALERT ------->|
    |                         |   (HIGH, need=160)    |
    |                         |                       |
                                          TransferCoordinationAgent
                                                      |
                                        <-- SHORTAGE_CLASSIFIED (HIGH, ESSENTIAL)
                                                      |
                                          [Search wards: ICU has 150, ratio=0.75 > 0.5]
                                          [150 > 160*0.5=80: donor valid]
                                          [transfer_qty = min(160, int(150*0.5)) = 75]
                                          [Update ICU: 150-75=75, SURGICAL: 40+75=115]
                                          [Create TR-003 COMPLETED]
                                                      |
                               ProcurementEscalationAgent
                                                      |
                               <-- TRANSFER_RESULT (success=True, TR-003)
                                  [Mark amoxicillin_SURGICAL RESOLVED]

Outcome: TR-003 COMPLETED, no procurement created
```

### Scenario 3b: Paracetamol GENERAL - Procurement Confirmation

```
Step 10
PharmacySensor          StockMonitorAgent     SupplyAssessmentAgent
    |                         |                       |
    |-- STOCK_READING ------->|                       |
    |   (paracetamol,         |                       |
    |    GENERAL, 160)        |-- STOCK_ALERT ------->|
    |                         |   (MEDIUM, need=340)  |
    |                         |                       |
                                         ProcurementEscalationAgent
                                                      |
                                        <-- SHORTAGE_CLASSIFIED (MEDIUM, STANDARD)
                                           [No await_transfer_result flag]
                                           [find_supplier("standard") -> BasicMeds]
                                           [create PR-002, dispatch_step=10]

Steps 11-13: proactive check, 10-10<5, no escalation

Step 14: Simulator calls simulate_supplier_confirmation("paracetamol_GENERAL", 14)
  ProcurementEscalationAgent:
  -> PR-002 status = CONFIRMED, confirmed_step = 14

Steps 15-20: PR-002 remains CONFIRMED, no escalation

Outcome: PR-002 CONFIRMED at step 14
```

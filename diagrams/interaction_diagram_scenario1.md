# MedStock — Interaction Diagram: Scenario 1
**Insulin ICU Critical Shortage — Transfer Success**
Student ID: 11126586 | Course: DCIT 403

> **Scenario:** At step 1, the ICU ward has only 8 units of Insulin (8% of threshold).
> The system detects the CRITICAL shortage, finds surplus in EMERGENCY (120 units),
> and transfers 60 units. No procurement is needed.

```mermaid
sequenceDiagram
    participant PS as PharmacySensor
    participant SM as StockMonitorAgent
    participant SA as SupplyAssessmentAgent
    participant TC as TransferCoordinationAgent
    participant PE as ProcurementEscalationAgent

    Note over PS,PE: ── STEP 1 ──

    PS->>SM: STOCK_READING<br/>drug=insulin · ward=ICU · qty=8

    Note over SM: set_stock(insulin, ICU, 8, step=1)<br/>ratio = 8 / 100 = 8% → CRITICAL<br/>not in alerted_stocks → add<br/>quantity_needed = 92

    SM->>SA: STOCK_ALERT<br/>severity=CRITICAL · quantity_needed=92

    Note over SA: shortage_id = insulin_ICU<br/>not in active_shortages → register<br/>category = ESSENTIAL<br/>Plan selected: CRITICAL

    SA->>PE: SHORTAGE_CLASSIFIED<br/>CRITICAL · ESSENTIAL · await_transfer_result=True
    SA->>TC: SHORTAGE_CLASSIFIED<br/>CRITICAL · ESSENTIAL

    Note over TC: category = ESSENTIAL — not CONTROLLED<br/>TransferSearchPlan: iterate all wards<br/>EMERGENCY: stock=120, ratio=120/100=1.2 > 0.5 ✓<br/>120 > 92 × 0.5 = 46 ✓ valid donor<br/>transfer_qty = min(92, int(120×0.5)) = 60<br/>EMERGENCY: 120 → 60<br/>ICU: 8 → 68<br/>Create TR-001 COMPLETED

    TC->>PE: TRANSFER_RESULT<br/>success=True · TR-001 · qty=60 · from=EMERGENCY

    Note over PE: insulin_ICU found in _awaiting_transfer<br/>success=True → move to resolved_shortages<br/>No procurement initiated

    Note over PS,PE: ── OUTCOME ──<br/>TR-001 COMPLETED (60 units Insulin · EMERGENCY → ICU)<br/>Shortage insulin_ICU: RESOLVED by transfer<br/>No procurement record created
```
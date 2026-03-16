# MedStock — Interaction Diagram: Scenario 3
**Amoxicillin SURGICAL (Transfer) + Paracetamol GENERAL (Procurement Confirmed)**
Student ID: 11126586 | Course: DCIT 403

> **Scenario 3a:** Step 8 — Amoxicillin SURGICAL (40 tablets, 20% = HIGH). Transfer from ICU (150 tablets) succeeds.
>
> **Scenario 3b:** Step 10 — Paracetamol GENERAL (160 tablets, 32% = MEDIUM). Procurement PR-002 via BasicMeds, confirmed at step 14.

```mermaid
sequenceDiagram
    participant PS as PharmacySensor
    participant SM as StockMonitorAgent
    participant SA as SupplyAssessmentAgent
    participant TC as TransferCoordinationAgent
    participant PE as ProcurementEscalationAgent

    Note over PS,PE: ── SCENARIO 3a · STEP 8: Amoxicillin SURGICAL ──

    PS->>SM: STOCK_READING<br/>drug=amoxicillin · ward=SURGICAL · qty=40

    Note over SM: ratio = 40 / 200 = 20% → HIGH<br/>quantity_needed = 160

    SM->>SA: STOCK_ALERT<br/>severity=HIGH · quantity_needed=160

    Note over SA: category = ESSENTIAL<br/>Plan selected: HIGH → TransferCoord only

    SA->>TC: SHORTAGE_CLASSIFIED<br/>HIGH · ESSENTIAL

    Note over TC: TransferSearchPlan: search all wards<br/>ICU: stock=150, ratio=150/200=0.75 > 0.5 ✓<br/>150 > 160 × 0.5 = 80 ✓ valid donor<br/>transfer_qty = min(160, int(150×0.5)) = 75<br/>ICU: 150 → 75 · SURGICAL: 40 → 115<br/>Create TR-003 COMPLETED

    TC->>PE: TRANSFER_RESULT<br/>success=True · TR-003 · qty=75 · from=ICU

    Note over PE: Mark amoxicillin_SURGICAL RESOLVED<br/>No procurement initiated

    Note over PS,PE: ── SCENARIO 3b · STEP 10: Paracetamol GENERAL ──

    PS->>SM: STOCK_READING<br/>drug=paracetamol · ward=GENERAL · qty=160

    Note over SM: ratio = 160 / 500 = 32% → MEDIUM<br/>quantity_needed = 340

    SM->>SA: STOCK_ALERT<br/>severity=MEDIUM · quantity_needed=340

    Note over SA: category = STANDARD<br/>Plan selected: MEDIUM → ProcurementEscalation only

    SA->>PE: SHORTAGE_CLASSIFIED<br/>MEDIUM · STANDARD · no await_transfer_result flag

    Note over PE: _initiate_procurement()<br/>find_supplier("standard") → BasicMeds Supplies<br/>Create PR-002 REQUESTED · dispatch_step=10

    loop Steps 11 – 13: proactive_step() each cycle
        Note over PE: elapsed = current_step − 10 < 5<br/>No escalation yet
    end

    Note over PE: Step 14: simulate_supplier_confirmation()<br/>PR-002 status=REQUESTED → CONFIRMED<br/>confirmed_step=14

    Note over PE: Steps 15–20: PR-002 already CONFIRMED<br/>No escalation triggered

    Note over PS,PE: ── OUTCOMES ──<br/>3a: TR-003 COMPLETED (75 tablets · ICU → SURGICAL) · amoxicillin_SURGICAL RESOLVED<br/>3b: PR-002 CONFIRMED at step 14 via BasicMeds Supplies
```

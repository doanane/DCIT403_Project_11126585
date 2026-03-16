# MedStock — Interaction Diagram: Scenario 2
**Morphine SURGICAL — Controlled Substance Policy + Escalation**
Student ID: 11126586 | Course: DCIT 403

> **Scenario:** At step 3, SURGICAL has 7 mg of Morphine (14% of threshold = HIGH severity).
> Morphine is CONTROLLED. Internal transfer is denied by regulatory policy.
> Procurement PR-001 is created at step 3. No confirmation arrives.
> Escalation occurs at step 8 (5 steps after dispatch).

```mermaid
sequenceDiagram
    participant PS as PharmacySensor
    participant SM as StockMonitorAgent
    participant SA as SupplyAssessmentAgent
    participant TC as TransferCoordinationAgent
    participant PE as ProcurementEscalationAgent

    Note over PS,PE: ── STEP 3 ──

    PS->>SM: STOCK_READING<br/>drug=morphine · ward=SURGICAL · qty=7

    Note over SM: ratio = 7 / 50 = 14% → HIGH<br/>not in alerted_stocks → add<br/>quantity_needed = 43

    SM->>SA: STOCK_ALERT<br/>severity=HIGH · quantity_needed=43

    Note over SA: shortage_id = morphine_SURGICAL<br/>category = CONTROLLED<br/>Plan selected: HIGH → TransferCoord only

    SA->>TC: SHORTAGE_CLASSIFIED<br/>HIGH · CONTROLLED

    Note over TC: drug.category = CONTROLLED<br/>ControlledDenialPlan: regulatory denial<br/>Create TR-002 FAILED · from_ward=N/A · qty=0

    TC->>PE: TRANSFER_RESULT<br/>success=False · reason=controlled_substance_policy

    Note over PE: not in _awaiting_transfer<br/>call _initiate_procurement()<br/>find_supplier("controlled") → PharmaControl Ltd<br/>Create PR-001 REQUESTED · dispatch_step=3

    loop Steps 4 – 7: proactive_step() each cycle
        Note over PE: elapsed = current_step − 3<br/>Step 4: 1 < 5 — no escalation<br/>Step 5: 2 < 5 — no escalation<br/>Step 6: 3 < 5 — no escalation<br/>Step 7: 4 < 5 — no escalation
    end

    Note over PE: Step 8: elapsed = 8 − 3 = 5 ≥ ESCALATION_TIMEOUT_STEPS<br/>PR-001 status → ESCALATED · escalated_step=8

    Note over PS,PE: ── OUTCOME ──<br/>TR-002 FAILED (controlled substance policy · from N/A)<br/>PR-001 ESCALATED at step 8 via PharmaControl Ltd<br/>morphine_SURGICAL shortage status: ESCALATED
```

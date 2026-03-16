# MedStock — Capability Overview: ProcurementEscalationAgent
**Prometheus Methodology Artifact**
Student ID: 11126586 | Course: DCIT 403

**Agent:** ProcurementEscalationAgent
**Role:** Terminal agent in the pipeline. Manages the full procurement lifecycle: initiation, tracking, proactive escalation, and supplier confirmation.

---

## Capability 1 & 2: Handle Incoming Messages

```mermaid
flowchart TD
    A([SHORTAGE_CLASSIFIED received])
    B{await_transfer_result\nflag present?}
    C[Store in _awaiting_transfer\nwait for TRANSFER_RESULT]
    D[Call _initiate_procurement]

    E([TRANSFER_RESULT received])
    F{success?}
    G[Move to resolved_shortages\nRemove from _awaiting_transfer\nLog: Transfer succeeded — resolved]
    H[Pop from _awaiting_transfer\nif present\nCall _initiate_procurement]

    A --> B
    B -->|Yes — CRITICAL| C
    B -->|No — MEDIUM| D

    E --> F
    F -->|True| G
    F -->|False| H
```

---

## Capability 3: InitiateProcurement — Internal Plan

```mermaid
flowchart TD
    IP([_initiate_procurement called])
    DC{shortage_id in\npending_procurements\nOR resolved_shortages?}
    SKIP([Return — duplicate\nno double procurement])
    CAT[category = content category lowercase\nis_controlled = category == controlled]
    SUP[supplier = supplier_db.find_supplier\ncategory]
    REC[record = supplier_db.create_procurement\ndrug_id · ward_id · qty · supplier · is_controlled]
    STORE([Store in pending_procurements\ndispatch_step = current_step\nstatus = REQUESTED])

    IP --> DC
    DC -->|Yes| SKIP
    DC -->|No| CAT --> SUP --> REC --> STORE
```

---

## Capability 4: ProactiveEscalation — Runs Every Cycle

```mermaid
flowchart TD
    PS([proactive_step called\nevery simulation cycle])
    FOR[For each shortage_id\nin pending_procurements]
    REQ{status == REQUESTED?}
    SKIP([Skip — already CONFIRMED\nor ESCALATED])
    ELAPSED[steps_elapsed =\ncurrent_step - dispatch_step]
    TIMEOUT{steps_elapsed\n>= 5\nESCALATION_TIMEOUT_STEPS?}
    CONT([Continue monitoring\nnext cycle])
    ESC([record.status = ESCALATED\nrecord.escalated_step = current_step\nLog: ESCALATION record_id drug ward])

    PS --> FOR --> REQ
    REQ -->|No| SKIP
    REQ -->|Yes| ELAPSED --> TIMEOUT
    TIMEOUT -->|No| CONT
    TIMEOUT -->|Yes| ESC
```

---

## Capability 5: ConfirmSupply — External Trigger

```mermaid
flowchart TD
    SC([simulate_supplier_confirmation\nshortageid · step called])
    IN{shortage_id in\npending_procurements?}
    NOOP([No action])
    SREQ{status == REQUESTED?}
    CONFIRM([status = CONFIRMED\nconfirmed_step = step\nLog confirmation])
    ALREADY([Already ESCALATED\nor CONFIRMED — no change])

    SC --> IN
    IN -->|No| NOOP
    IN -->|Yes| SREQ
    SREQ -->|Yes| CONFIRM
    SREQ -->|No| ALREADY
```

---

## Escalation Timeline Example — Morphine SURGICAL

| Step | elapsed = current − dispatch | Outcome |
|---|---|---|
| 3 | 0 | PR-001 created (dispatch_step=3) |
| 4 | 1 < 5 | No escalation |
| 5 | 2 < 5 | No escalation |
| 6 | 3 < 5 | No escalation |
| 7 | 4 < 5 | No escalation |
| 8 | **5 ≥ 5** | **PR-001 → ESCALATED** |

---

## Percepts, Beliefs, Actions

| Type | Detail |
|---|---|
| **Percepts** | SHORTAGE_CLASSIFIED (from SupplyAssessment); TRANSFER_RESULT (from TransferCoord); simulate_supplier_confirmation() (from Simulator at step 14) |
| **Belief: SupplierDatabase** | find_supplier(category) → Supplier; create_procurement → ProcurementRecord; get_all_procurements |
| **Belief: pending_procurements** | dict[shortage_id → tracking dict] — dispatch_step, status, record |
| **Belief: resolved_shortages** | dict[shortage_id → resolution info] |
| **Belief: _awaiting_transfer** | dict[shortage_id → shortage_info] — holds CRITICAL cases waiting for transfer result |
| **Action** | supplier_db.create_procurement() — create ProcurementRecord (PR-001 format) |
| **Action** | Update record.status to ESCALATED or CONFIRMED |
| **Action** | Log escalation and confirmation events via log_callback |

# MedStock — Capability Overview: SupplyAssessmentAgent
**Prometheus Methodology Artifact**
Student ID: 11126586 | Course: DCIT 403

**Agent:** SupplyAssessmentAgent
**Role:** Classification and routing agent. Selects the appropriate response plan based on shortage severity and drug category.

---

## Capability: ClassifyShortage — Plan Flow

```mermaid
flowchart TD
    A([STOCK_ALERT received\nfrom StockMonitorAgent])
    B[1. shortage_id = drug_id + _ + ward_id]
    C{2. shortage_id already\nin active_shortages?}
    D([Duplicate — return immediately\nno reprocessing])
    E[3. drug = drug_db.get_drug\ncategory = drug.category.value\nBuild shortage_info dict\nactive_shortages[shortage_id] = info]
    F{4. Plan selection\nbased on severity}

    CRIT_A[CRITICAL plan\nSend SHORTAGE_CLASSIFIED\nto TransferCoordinationAgent]
    CRIT_B[CRITICAL plan\nSend SHORTAGE_CLASSIFIED\nto ProcurementEscalationAgent\nawait_transfer_result=True]
    HIGH_A[HIGH plan\nSend SHORTAGE_CLASSIFIED\nto TransferCoordinationAgent ONLY\ntransfer-first policy]
    MED_A[MEDIUM plan\nSend SHORTAGE_CLASSIFIED\nto ProcurementEscalationAgent ONLY\ndirect procurement watch]

    A --> B --> C
    C -->|Yes| D
    C -->|No| E --> F
    F -->|CRITICAL| CRIT_A
    F -->|CRITICAL| CRIT_B
    F -->|HIGH| HIGH_A
    F -->|MEDIUM| MED_A
```

---

## Percepts, Beliefs, Actions

| Type | Detail |
|---|---|
| **Percept** | STOCK_ALERT — drug_id, ward_id, current_stock, reorder_threshold, severity, quantity_needed, step |
| **Belief: DrugDatabase** | get_drug(drug_id) → Drug with .category field |
| **Belief: active_shortages** | dict[shortage_id → shortage_info] — duplicate prevention |
| **Action** | Register in active_shortages |
| **Action** | Send SHORTAGE_CLASSIFIED to TransferCoordinationAgent (CRITICAL or HIGH) |
| **Action** | Send SHORTAGE_CLASSIFIED to ProcurementEscalationAgent (CRITICAL with await=True, or MEDIUM) |

### SHORTAGE_CLASSIFIED Content
`shortage_id · drug_id · drug_name · ward_id · severity · category · current_stock · reorder_threshold · quantity_needed · step · [await_transfer_result: bool — CRITICAL to procurement only]`

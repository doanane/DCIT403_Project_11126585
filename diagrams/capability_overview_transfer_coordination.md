# MedStock — Capability Overview: TransferCoordinationAgent
**Prometheus Methodology Artifact**
Student ID: 11126586 | Course: DCIT 403

**Agent:** TransferCoordinationAgent
**Role:** Inter-ward transfer agent. Enforces controlled substance policy. Searches for surplus donor wards and executes stock transfers.

---

## Capability: CoordinateTransfer — Plan Flow

```mermaid
flowchart TD
    A([SHORTAGE_CLASSIFIED received\nfrom SupplyAssessmentAgent])
    B[1. drug = drug_db.get_drug\ndrug_id]
    C{2. drug.category\n== CONTROLLED?}

    subgraph CDP["ControlledDenialPlan"]
        D1[Log: regulatory denial\nno internal transfer permitted]
        D2[Create TransferRecord\nstatus=FAILED · from_ward=N/A · qty=0]
        D3([Send TRANSFER_RESULT\nsuccess=False\nreason=controlled_substance_policy])
        D1 --> D2 --> D3
    end

    subgraph TSP["TransferSearchPlan"]
        E1[Iterate all wards\nexcluding shortage ward]
        E2[For each ward:\nstock = get_stock drug_id · ward_id\nsurplus_ratio = stock / reorder_threshold]
        E3{Donor valid?\nsurplus_ratio > 0.5\nAND stock > qty_needed × 0.5}
        E4([No donor found\nCreate TransferRecord FAILED\nSend TRANSFER_RESULT success=False\nreason=no_donor_available])
        E5[transfer_qty =\nmin qty_needed · int donor_stock × 0.5]
        E6[Update stocks:\ndonor_stock -= transfer_qty\nrecipient_stock += transfer_qty]
        E7[Create TransferRecord COMPLETED]
        E8([Send TRANSFER_RESULT\nsuccess=True\ntransfer_id · transfer_qty · from_ward])
        E1 --> E2 --> E3
        E3 -->|No| E4
        E3 -->|Yes| E5 --> E6 --> E7 --> E8
    end

    A --> B --> C
    C -->|Yes| CDP
    C -->|No| TSP
```

---

## Percepts, Beliefs, Actions

| Type | Detail |
|---|---|
| **Percept** | SHORTAGE_CLASSIFIED — shortage_id, drug_id, drug_name, ward_id, severity, category, current_stock, reorder_threshold, quantity_needed, step |
| **Belief: DrugDatabase** | get_drug, get_stock, set_stock — reads all ward stocks, writes both donor and recipient after transfer |
| **Belief: WardDatabase** | get_all_wards → list of Ward; create_transfer → TransferRecord |
| **Action: set_stock()** | Update stock levels for both donor and recipient wards |
| **Action: create_transfer()** | Write TransferRecord (TR-001 format) with COMPLETED or FAILED status |
| **Action: send TRANSFER_RESULT** | Notify ProcurementEscalationAgent of outcome |

### TRANSFER_RESULT Content
**On success:** `shortage_id · drug_id · drug_name · ward_id · success=True · severity · category · quantity_needed · step · transfer_id · transfer_qty · from_ward`

**On failure:** `shortage_id · drug_id · drug_name · ward_id · success=False · reason · severity · category · quantity_needed · step`

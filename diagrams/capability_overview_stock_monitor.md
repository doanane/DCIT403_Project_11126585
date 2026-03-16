# MedStock — Capability Overview: StockMonitorAgent
**Prometheus Methodology Artifact**
Student ID: 11126586 | Course: DCIT 403

**Agent:** StockMonitorAgent
**Role:** First-level reactive monitoring agent. Receives all sensor data.

---

## Capability: MonitorStock — Plan Flow

```mermaid
flowchart TD
    A([STOCK_READING received\nfrom PharmacySensor])
    B[1. drug_db.set_stock\ndrug_id · ward_id · quantity · step]
    C[2. record = drug_db.get_stock\ndrug = drug_db.get_drug\nsev = record.severity]
    D[3. Log: stock reading\ndrug · ward · qty · pct · severity]
    E{4. severity is\nCRITICAL / HIGH / MEDIUM?}
    F{already in\nalerted_stocks?}
    G([LOW or OK\nNo action needed])
    H([Duplicate suppressed\nNo action])
    I[Add to alerted_stocks\ncompute quantity_needed\n= threshold - current_stock]
    J([Send STOCK_ALERT\nto SupplyAssessmentAgent])

    A --> B --> C --> D --> E
    E -->|No — LOW or OK| G
    E -->|Yes| F
    F -->|Yes — duplicate| H
    F -->|No — new alert| I --> J
```

---

## Severity Logic — StockRecord.severity()

```mermaid
flowchart TD
    R([ratio = current_stock / reorder_threshold])
    C1{ratio < 0.10?}
    C2{ratio < 0.30?}
    C3{ratio < 0.50?}
    C4{ratio < 0.75?}
    CRIT([CRITICAL — alert])
    HIGH([HIGH — alert])
    MED([MEDIUM — alert])
    LOW([LOW — no alert])
    OK([OK — no alert])

    R --> C1
    C1 -->|Yes| CRIT
    C1 -->|No| C2
    C2 -->|Yes| HIGH
    C2 -->|No| C3
    C3 -->|Yes| MED
    C3 -->|No| C4
    C4 -->|Yes| LOW
    C4 -->|No| OK
```

---

## Percepts, Beliefs, Actions

| Type | Detail |
|---|---|
| **Percept** | STOCK_READING — drug_id, ward_id, quantity, step — from PharmacySensor |
| **Belief: DrugDatabase** | drugs: dict[drug_id → Drug]; stocks: dict[(drug_id, ward_id) → StockRecord] |
| **Belief: alerted_stocks** | set of (drug_id, ward_id) tuples — duplicate suppression |
| **Action: set_stock()** | Update DrugDatabase with sensor-reported quantity |
| **Action: send STOCK_ALERT** | Notify SupplyAssessmentAgent of detected shortage |

### STOCK_ALERT Content
`drug_id · ward_id · current_stock · reorder_threshold · severity · quantity_needed · step`

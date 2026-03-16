# MedStock — System Overview Diagram
**Prometheus Methodology Artifact**
Student ID: 11126586 | Course: DCIT 403

```mermaid
graph TD
    subgraph ENV["ENVIRONMENT LAYER — Shared Data Stores"]
        DB1[(DrugDatabase\n5 drugs · 25 stock records)]
        DB2[(WardDatabase\n5 wards · Transfer records)]
        DB3[(SupplierDatabase\n3 suppliers · Procurement records)]
    end

    subgraph SENSOR["SENSOR LAYER"]
        PS[PharmacySensor\nStep  1 → insulin    ICU      qty=8\nStep  3 → morphine   SURGICAL qty=7\nStep  8 → amoxicillin SURGICAL qty=40\nStep 10 → paracetamol GENERAL  qty=160]
    end

    subgraph AGENTS["AGENT LAYER"]
        SMA[StockMonitorAgent\nReceives STOCK_READING\nComputes severity level\nMaintains alerted_stocks\nSends STOCK_ALERT]
        SAA[SupplyAssessmentAgent\nReceives STOCK_ALERT\nClassifies by drug category\nSelects response plan\nMaintains active_shortages]
        TCA[TransferCoordinationAgent\nEnforces CONTROLLED policy\nFinds surplus donor ward\nExecutes inter-ward transfer\nSends TRANSFER_RESULT]
        PEA[ProcurementEscalationAgent\nAwaits transfer result\nInitiates procurement\nProactive escalation every cycle\nConfirms supplier deliveries]
    end

    subgraph UI["UI LAYER"]
        APP[MedStockApp — Tkinter\nStep counter · Step / Auto / Reset buttons\nPanel 1: Drug Stock Levels colour-coded\nPanel 2: Active Alerts severity-tagged\nPanel 3: Transfers and Procurement records\nPanel 4: Activity Log agent-colour-coded\nStatus Bar: step / alert / transfer / proc counts]
    end

    PS -->|STOCK_READING| SMA
    SMA -->|STOCK_ALERT| SAA
    SAA -->|SHORTAGE_CLASSIFIED\nCRITICAL or HIGH| TCA
    SAA -->|SHORTAGE_CLASSIFIED\nCRITICAL or MEDIUM\nawait_transfer=True on CRITICAL| PEA
    TCA -->|TRANSFER_RESULT| PEA

    SMA <-->|read / write stocks| DB1
    SAA <-->|read drug category| DB1
    TCA <-->|read all ward stocks\nwrite after transfer| DB1
    TCA <-->|write TransferRecords\nread ward list| DB2
    PEA <-->|read suppliers\nwrite ProcurementRecords| DB3
```

---

## Key Constants

| Constant | Value | Purpose |
|---|---|---|
| ESCALATION_TIMEOUT_STEPS | 5 | Steps without confirmation before escalation |
| SENSOR_SCHEDULE | Steps 1, 3, 8, 10 | Pre-scheduled PharmacySensor events |
| SUPPLIER_CONFIRMATION | Step 14 | paracetamol_GENERAL confirmation injection |
| TOTAL_STEPS | 20 | Simulation duration |

---

## Drugs and Wards

| Drug | Category | Threshold |
|---|---|---|
| Insulin | ESSENTIAL | 100 units |
| Morphine | CONTROLLED | 50 mg |
| Amoxicillin | ESSENTIAL | 200 tablets |
| Paracetamol | STANDARD | 500 tablets |
| IV Fluids | ESSENTIAL | 300 units |

| Ward | Priority |
|---|---|
| ICU | 5 (highest) |
| Emergency | 4 |
| Surgical | 3 |
| Maternity | 2 |
| General | 1 |
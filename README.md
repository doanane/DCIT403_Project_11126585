# MedStock
## Hospital Pharmacy Stock Depletion and Emergency Resupply Coordination

**Student ID:** 11126586
**Course:** DCIT 403 - Intelligent Agent Systems
**Methodology:** Prometheus (Padgham and Winikoff, 2004)

---

## Project Overview

MedStock is a multi-agent system that monitors drug stock levels across five hospital wards, detects critical and high-severity shortages, coordinates internal ward transfers where surplus stock exists, initiates emergency procurement orders from approved suppliers, escalates unconfirmed orders after a configurable timeout, and proactively tracks batch expiry to ensure near-expiry drugs are used first (FEFO). The system is built using the Prometheus agent design methodology and implemented in Python 3 using the standard library only.

---

## System Architecture

The system contains five intelligent agents communicating through a central message-passing infrastructure:

| Agent | Role |
|---|---|
| StockMonitorAgent | Receives sensor readings, classifies severity, sends stock alerts |
| SupplyAssessmentAgent | Classifies shortage by drug category, selects response plan |
| TransferCoordinationAgent | Searches for donor wards, executes transfers, enforces controlled substance policy |
| ProcurementEscalationAgent | Initiates procurement, tracks orders, proactively escalates overdue procurement |
| ExpiryMonitorAgent | Scans all ward drug batches each step, flags expired/expiring stock, enforces FEFO, escalates expiry alerts |

Messages flow in this direction:

```
PharmacySensor -> StockMonitorAgent -> SupplyAssessmentAgent -> TransferCoordinationAgent
                                                              -> ProcurementEscalationAgent
                                       TransferCoordinationAgent -> ProcurementEscalationAgent
ExpiryMonitorAgent -> ProcurementEscalationAgent (EXPIRY_ALERT)
```

---

## Setup and Run

1. Ensure Python 3 is installed.
2. Activate the virtual environment:
   ```
   .venv/Scripts/activate
   ```
3. Run the application:
   ```
   .venv/Scripts/python main.py
   ```

No external packages are required. All dependencies are from the Python standard library.

---

## Project Structure

```
DCIT403_Project_11126586/
├── main.py                          Entry point. Launches the MedStockApp tkinter window.
├── requirements.txt                 Lists tkinter as the only dependency (stdlib).
├── README.md                        This file.
│
├── src/                             All backend source code.
│   ├── __init__.py
│   ├── core/                        Agent infrastructure (framework-level code).
│   │   ├── __init__.py
│   │   ├── message.py               Performative enum and Message dataclass.
│   │   ├── agent.py                 Base Agent class: inbox, send/receive, run_cycle.
│   │   └── agent_system.py          AgentSystem: agent registry and message delivery.
│   │
│   ├── agents/                      The five domain-specific agents.
│   │   ├── __init__.py
│   │   ├── stock_monitor_agent.py   Detects shortages from sensor readings.
│   │   ├── supply_assessment_agent.py  Classifies and routes shortage notifications.
│   │   ├── transfer_coordination_agent.py  Coordinates inter-ward drug transfers.
│   │   ├── procurement_escalation_agent.py  Manages procurement and escalation.
│   │   └── expiry_monitor_agent.py  Monitors all batch expiry dates and enforces FEFO use order.
│   │
│   ├── beliefs/                     Data model classes (beliefs in Prometheus terms).
│   │   ├── __init__.py
│   │   ├── drug_belief.py           Drug, StockRecord, ExpiryBatch, DrugDatabase, DrugCategory, SeverityLevel, ExpiryStatus.
│   │   ├── ward_belief.py           Ward, TransferRecord, WardDatabase, TransferStatus.
│   │   └── supplier_belief.py       Supplier, ProcurementRecord, SupplierDatabase, ProcurementStatus.
│   │
│   ├── environment/                 Environment objects that emit percepts.
│   │   ├── __init__.py
│   │   └── pharmacy_sensor.py       PharmacySensor: schedules and emits STOCK_READING messages.
│   │
│   └── simulation/                  Simulation orchestration.
│       ├── __init__.py
│       └── simulator.py             MedStockSimulator: initialises all agents, runs steps.
│
├── ui/                              Graphical user interface (tkinter).
│   ├── __init__.py
│   ├── theme.py                     COLORS and FONTS constants for consistent styling.
│   └── app.py                       MedStockApp: full tkinter UI with 4 panels.
│
├── docs/                            Prometheus methodology documentation.
│   ├── phase1_system_specification.md
│   ├── phase2_architectural_design.md
│   ├── phase3_interaction_design.md
│   ├── phase4_detailed_design.md
│   └── phase5_report.md
│
└── diagrams/                        ASCII art design diagrams.
    ├── goal_hierarchy.txt
    ├── system_overview.txt
    ├── acquaintance_diagram.txt
    ├── interaction_diagram_scenario1.txt
    ├── interaction_diagram_scenario2.txt
    ├── interaction_diagram_scenario3.txt
    ├── capability_overview_stock_monitor.txt
    ├── capability_overview_supply_assessment.txt
    ├── capability_overview_transfer_coordination.txt
    └── capability_overview_procurement_escalation.txt
```

---

## Simulation Scenarios

The simulation runs for 20 steps. Four sensor events are scheduled:

| Step | Drug | Ward | Quantity | Severity | Outcome |
|---|---|---|---|---|---|
| 1 | Insulin | ICU | 8 units | CRITICAL | Transfer TR-001 from EMERGENCY (60 units) |
| 3 | Morphine | SURGICAL | 7 mg | HIGH | Transfer denied (controlled); PR-001 escalated at step 8 |
| 8 | Amoxicillin | SURGICAL | 40 tablets | HIGH | Transfer TR-003 from ICU (75 tablets) |
| 10 | Paracetamol | GENERAL | 160 tablets | MEDIUM | PR-002 from BasicMeds, confirmed at step 14 |

In addition to these shortage scenarios, the simulator seeds expiry-tracked batches for every drug/ward stock record (split into two lots per record). The ExpiryMonitorAgent scans these every step, marks WARNING / EXPIRING_SOON / EXPIRED states, and enforces FEFO ordering per drug+ward.

---

## Key Design Decisions

**Controlled substance policy:** Morphine and other CONTROLLED drugs are never transferred between wards. The TransferCoordinationAgent immediately sends TRANSFER_RESULT(success=False) when it detects a CONTROLLED drug, triggering procurement instead.

**CRITICAL plan:** When severity is CRITICAL, the SupplyAssessmentAgent sends SHORTAGE_CLASSIFIED to both the transfer and procurement agents simultaneously. The procurement agent holds off (await_transfer_result=True) until it learns whether the transfer succeeded. If it did, no procurement is created.

**Proactive escalation:** The ProcurementEscalationAgent calls _plan_check_and_escalate() every simulation cycle regardless of whether any messages were received. This ensures that overdue procurement orders are always detected.

**Expiry escalation and FEFO:** The ExpiryMonitorAgent proactively scans all tracked ward batches each cycle. EXPIRED and EXPIRING_SOON batches raise EXPIRY_ALERT messages to ProcurementEscalationAgent. FEFO is enforced in the stock model: when stock drops, depletion is applied against the earliest-expiring batch first.

**Duplicate suppression:** The StockMonitorAgent maintains an alerted_stocks set to avoid sending the same alert twice. The SupplyAssessmentAgent maintains an active_shortages dict keyed by shortage_id to avoid classifying the same shortage twice. The ProcurementEscalationAgent checks both pending_procurements and resolved_shortages before creating a new procurement record and ignores duplicate expiry status updates per batch. The ExpiryMonitorAgent tracks already-logged alert states to avoid log flooding.

---

## Prometheus Methodology Mapping

| Prometheus Phase | Implementation |
|---|---|
| Phase 1: System Specification | docs/phase1_system_specification.md, scenario data in simulator.py |
| Phase 2: Architectural Design | src/agents/ (5 agents), src/core/ (message infrastructure), acquaintance_diagram.txt |
| Phase 3: Interaction Design | Message dataclass, Performative enum, interaction diagram files |
| Phase 4: Detailed Design | Agent plan methods (_plan_*), belief classes in src/beliefs/, capability diagrams |
| Phase 5: Report | docs/phase5_report.md |

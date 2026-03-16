---
marp: true
theme: default
paginate: true
backgroundColor: #ffffff
color: #1C1C1C
style: |
  section {
    font-family: 'Segoe UI', Calibri, sans-serif;
    font-size: 22px;
    padding: 50px 60px;
  }
  h1 {
    color: #1A3C6B;
    font-size: 40px;
    border-bottom: 4px solid #0D6E6E;
    padding-bottom: 10px;
    margin-bottom: 20px;
  }
  h2 {
    color: #0D6E6E;
    font-size: 28px;
    margin-bottom: 12px;
  }
  h3 {
    color: #1A3C6B;
    font-size: 22px;
    margin-bottom: 8px;
  }
  section.cover {
    background: linear-gradient(135deg, #1A3C6B 0%, #0D6E6E 100%);
    color: #ffffff;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
  }
  section.cover h1 {
    color: #ffffff;
    border-bottom: 3px solid rgba(255,255,255,0.5);
    font-size: 56px;
  }
  section.cover h2 {
    color: rgba(255,255,255,0.85);
    font-size: 24px;
  }
  section.cover p {
    color: rgba(255,255,255,0.75);
    font-size: 18px;
  }
  section.phase {
    background: #F0F7FF;
  }
  section.phase h1 {
    color: #1A3C6B;
  }
  section.agent {
    border-left: 6px solid #0D6E6E;
    padding-left: 54px;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 17px;
  }
  th {
    background: #1A3C6B;
    color: white;
    padding: 8px 12px;
    text-align: left;
  }
  td {
    padding: 7px 12px;
    border-bottom: 1px solid #dde;
  }
  tr:nth-child(even) td {
    background: #EBF5FB;
  }
  ul {
    margin: 8px 0;
    padding-left: 26px;
  }
  li {
    margin-bottom: 6px;
    line-height: 1.5;
  }
  .tag {
    background: #1A3C6B;
    color: white;
    border-radius: 4px;
    padding: 2px 10px;
    font-size: 14px;
    font-weight: bold;
    margin-right: 6px;
  }
  blockquote {
    background: #E8F0FE;
    border-left: 5px solid #1A3C6B;
    padding: 12px 18px;
    border-radius: 4px;
    font-style: normal;
    color: #1A3C6B;
  }
---

<!-- _class: cover -->

# MedStock

## Hospital Pharmacy Stock Depletion
## and Emergency Resupply Coordination

---

**DCIT 403 — Intelligent Agent Systems**
Prometheus Methodology (Padgham & Winikoff, 2004)
Student ID: 11126586

---

# The Problem

> Hospital pharmacies lose critical drugs before anyone notices.
> By the time a nurse finds an empty shelf, the patient may already be in danger.

**Root cause:** Information failure, not procurement failure

- Manual stock-take processes and handwritten ledgers
- No automatic detection when stock falls below safe levels
- No mechanism to check neighbouring wards for surplus
- No escalation system for unconfirmed supplier orders

---

# Why Multi-Agent?

| Property | How MedStock achieves it |
|---|---|
| **Reactivity** | Sensor readings arrive asynchronously; each must trigger immediate classification |
| **Proactivity** | ProcurementEscalationAgent checks all pending orders every cycle — no external trigger |
| **Social ability** | 5 agents mirror real hospital departments; communicate via structured messages |
| **Situatedness** | Agents perceive ward stocks, act on databases, trigger supplier-facing procurement |

---

# System at a Glance

- **5 hospital wards:** ICU, Emergency, Surgical, Maternity, General
- **5 drugs tracked:** Insulin, Morphine, Amoxicillin, Paracetamol, Metformin
- **3 approved suppliers:** MedPharm Ghana, PharmaControl Ltd, BasicMeds Supplies
- **5 intelligent agents** coordinated via message-passing
- **Python 3, standard library only** — runs on any lab computer
- **Tkinter GUI** for real-time simulation control and visualisation

---

<!-- _class: phase -->

# Prometheus Methodology

5 phases from specification to working code

| Phase | Focus |
|---|---|
| **Phase 1** | System Specification — goals, functionalities, scenarios |
| **Phase 2** | Architectural Design — agent types, acquaintance diagram |
| **Phase 3** | Interaction Design — messages, interaction diagrams |
| **Phase 4** | Detailed Design — capabilities, plans, belief structures |
| **Phase 5** | Implementation Report — code mapping, challenges |

---

<!-- _class: phase -->

# Phase 1 — System Specification

**Top-Level Goal:**
Ensure continuous availability of critical pharmaceutical supplies by automatically detecting shortages, coordinating transfers, initiating procurement, and escalating overdue orders.

**5 Sub-Goals:**

| | |
|---|---|
| G1 | Monitor drug stock levels across all wards |
| G2 | Classify shortages by clinical priority and drug category |
| G3 | Coordinate internal ward transfers for non-controlled drugs |
| G4 | Initiate emergency procurement from approved suppliers |
| G5 | Escalate overdue procurement orders proactively |

---

<!-- _class: phase -->

# Phase 1 — Severity Thresholds

| Severity | Condition | Response Plan |
|---|---|---|
| **CRITICAL** | Stock < 10% of threshold | Transfer + Procurement in parallel |
| **HIGH** | Stock 10 – 30% | Transfer first; procurement if transfer fails |
| **MEDIUM** | Stock 30 – 50% | Direct procurement (no transfer attempted) |
| LOW / OK | Stock > 50% | No action |

**19 functionalities (F1 – F19)** cover all detection, routing, transfer, procurement, escalation, audit trail, and supplier confirmation requirements.

---

<!-- _class: phase -->

# Phase 2 — Architectural Design

```
PharmacySensor
      |  STOCK_READING
      v
StockMonitorAgent
      |  STOCK_ALERT
      v
SupplyAssessmentAgent
      |  SHORTAGE_CLASSIFIED        |  SHORTAGE_CLASSIFIED
      v                             v
TransferCoordinationAgent    ProcurementEscalationAgent
      |  TRANSFER_RESULT            ^
      +-----------------------------+

ExpiryMonitorAgent ------------> ProcurementEscalationAgent
              EXPIRY_ALERT
```

Communication is **strictly directional** — no agent sends back to a higher-level agent except via TRANSFER_RESULT.

---

<!-- _class: phase -->

# Phase 3 — Interaction Design

**8 message performatives:**

| Performative | Flow |
|---|---|
| STOCK_READING | Sensor → StockMonitor |
| STOCK_ALERT | StockMonitor → SupplyAssessment |
| SHORTAGE_CLASSIFIED | SupplyAssessment → Transfer / Procurement |
| TRANSFER_RESULT | Transfer → Procurement |
| EXPIRY_ALERT | ExpiryMonitor → Procurement |
| PROCUREMENT_REQUEST | Internal procurement record |
| ESCALATION_NOTICE | Internal escalation record |
| STATUS_UPDATE | Reserved for future use |

---

<!-- _class: phase -->

# Phase 4 — Plan Selection

**SupplyAssessmentAgent plans:**

| Plan | Condition | Action |
|---|---|---|
| CRITICAL_plan | severity == CRITICAL | Send to Transfer AND Procurement (await=True) |
| HIGH_plan | severity == HIGH | Send to Transfer only |
| MEDIUM_plan | severity == MEDIUM | Send to Procurement only |

**TransferCoordinationAgent plans:**

| Plan | Condition | Action |
|---|---|---|
| ControlledDenialPlan | drug.category == CONTROLLED | Deny transfer; send TRANSFER_RESULT(success=False) |
| TransferSearchPlan | drug.category != CONTROLLED | Search wards; execute transfer or report failure |

---

# The 5 Agents

---

<!-- _class: agent -->

## StockMonitorAgent

**Role:** Entry point for all environmental data

- Receives STOCK_READING from PharmacySensor every step
- Computes `ratio = current_stock / reorder_threshold`
- Classifies: CRITICAL (<10%) | HIGH (10–30%) | MEDIUM (30–50%)
- Sends STOCK_ALERT to SupplyAssessmentAgent
- **alerted_stocks** set prevents duplicate alerts for same (drug, ward) pair

**Goals:** G1.1 — G1.4

---

<!-- _class: agent -->

## SupplyAssessmentAgent

**Role:** Central classifier and plan router

- Receives STOCK_ALERT; determines drug category
- Selects from 3 response plans based on severity
- **CRITICAL:** send to both agents (await_transfer_result=True to Procurement)
- **HIGH:** send to TransferCoordination only
- **MEDIUM:** send to ProcurementEscalation only
- **active_shortages** dict prevents re-classifying the same shortage

**Goals:** G2.1 — G2.4

---

<!-- _class: agent -->

## TransferCoordinationAgent

**Role:** Inter-ward stock transfer with regulatory enforcement

- Receives SHORTAGE_CLASSIFIED
- If CONTROLLED drug → immediate denial (regulatory policy)
- Otherwise, searches all wards for a valid donor:
  - `surplus_ratio > 0.5` AND `stock > quantity_needed × 0.5`
  - `transfer_qty = min(quantity_needed, int(donor_stock × 0.5))`
- Updates both donor and recipient stocks in DrugDatabase
- Creates TransferRecord (TR-001 format) with full audit trail
- Sends TRANSFER_RESULT(success, transfer_id, from_ward)

**Goals:** G3.1 — G3.5

---

<!-- _class: agent -->

## ProcurementEscalationAgent

**Role:** Full procurement lifecycle with proactive escalation

- **On SHORTAGE_CLASSIFIED (await=True):** store and wait for transfer outcome
- **On SHORTAGE_CLASSIFIED (MEDIUM):** initiate procurement immediately
- **On TRANSFER_RESULT (success=False):** initiate procurement
- **On TRANSFER_RESULT (success=True):** mark shortage resolved, no procurement
- **Every cycle (proactive_step):** check elapsed steps for all pending orders
  - If `current_step - dispatch_step >= 5` → status = **ESCALATED**
- Supplier confirmation sets status to **CONFIRMED**

**Goals:** G4.1 — G4.4, G5.1 — G5.3

---

<!-- _class: agent -->

## ExpiryMonitorAgent

**Role:** Batch expiry monitoring and FEFO enforcement

- Runs **proactively every cycle** — no incoming messages required
- Scans all drug batches across all wards
- Classifies each batch by `steps_remaining = expiry_step - current_step`:
  - `<= 0` → **EXPIRED**
  - `<= 3` → **EXPIRING_SOON**
  - `<= 6` → **WARNING**
- Sends EXPIRY_ALERT to ProcurementEscalationAgent for urgent batches
- Enforces **FEFO**: `_consume_batches_fefo()` always consumes earliest-expiring batches first

---

# 3 Simulation Scenarios

---

# Scenario 1 — Insulin ICU (Transfer Success)

**Step 1:** Insulin / ICU = 8 units (threshold 100 → **8% → CRITICAL**)

1. StockMonitor → STOCK_ALERT (CRITICAL, need 92 units)
2. SupplyAssessment → SHORTAGE_CLASSIFIED to **both** agents (await_transfer_result=True)
3. TransferCoord finds Emergency ward: 120 units, ratio 1.2 > 0.5
4. Transfers 60 units: Emergency 120 → 60 | ICU 8 → 68
5. TRANSFER_RESULT(success=True, **TR-001**)
6. Procurement marks shortage **RESOLVED** — no procurement created

---

# Scenario 2 — Morphine Surgical (Controlled + Escalation)

**Step 3:** Morphine / Surgical = 7 mg (threshold 50 → **14% → HIGH**)

1. SupplyAssessment → TransferCoord only (HIGH plan)
2. TransferCoord: **CONTROLLED** drug — regulatory denial
3. TRANSFER_RESULT(success=False, **TR-002**, reason: controlled_substance_policy)
4. ProcurementEscalation creates **PR-001** via PharmaControl Ltd; dispatch_step = 3
5. Steps 4–7: proactive check: 8–3 < 5, no escalation
6. **Step 8:** 8–3 = 5 ≥ timeout → **PR-001 ESCALATED**

---

# Scenario 3 — Multi-Drug Shortages

**Step 8:** Amoxicillin / Surgical = 40 tabs (200 threshold → **20% → HIGH**)
- ICU donor: 150 tabs, ratio 0.75 → transfer 75 tabs → **TR-003 COMPLETED**

**Step 10:** Paracetamol / General = 160 tabs (500 threshold → **32% → MEDIUM**)
- Direct procurement (no transfer) → **PR-002** via BasicMeds; dispatch_step = 10

**Step 14:** Supplier confirmation arrives → **PR-002 CONFIRMED**

---

# Phase 5 — Implementation

All 19 functionalities implemented. All 3 scenarios verified.

| Design Artefact | Python Implementation |
|---|---|
| Agent types (Phase 2) | 5 classes inheriting from `Agent` in `src/agents/` |
| Acquaintance diagram (Phase 2) | `AgentSystem` registry; hard-coded recipient strings |
| Message performatives (Phase 3) | `Performative` enum + `Message` dataclass in `src/core/message.py` |
| Belief structures (Phase 4) | `DrugDatabase`, `WardDatabase`, `SupplierDatabase` in `src/beliefs/` |
| Plan context conditions (Phase 4) | `if/elif` chains in `_plan_classify_shortage()` and `_plan_coordinate_transfer()` |
| Proactive escalation (Phase 4) | `proactive_step()` called after inbox processing every cycle |
| Scenarios (Phase 1) | `MedStockSimulator._schedule_sensor_events()` in `src/simulation/simulator.py` |

---

# Key Design Decisions

**1. CRITICAL shortage synchronisation**

> The _awaiting_transfer dict allows ProcurementEscalationAgent to hold a pending CRITICAL shortage without blocking. It only calls _initiate_procurement() when TRANSFER_RESULT arrives with success=False.

**2. Controlled substance policy**

> TransferCoordinationAgent checks drug.category before searching for a donor. CONTROLLED drugs trigger an immediate FAILED transfer record — regulatory compliance is hard-coded.

**3. Standard library only**

> No package manager required. Dataclasses and enums map directly to Prometheus belief structures. Tkinter provides the GUI without any external dependency.

---

# Architecture Summary

```
src/
  core/         message.py | agent.py | agent_system.py
  agents/       5 agent files
  beliefs/      drug_belief.py | ward_belief.py | supplier_belief.py
  environment/  pharmacy_sensor.py
  simulation/   simulator.py
ui/             app.py (Tkinter)
docs/           phase1 – phase5 | presentation guide
diagrams/       10 ASCII art diagrams
main.py         entry point
```

**Key constants:**
- `ESCALATION_TIMEOUT_STEPS = 5`
- `EXPIRING_SOON_THRESHOLD = 3`
- `TOTAL_STEPS = 20`

---

<!-- _class: cover -->

# Conclusion

MedStock demonstrates that the **Prometheus methodology** produces a coherent, verifiable, and extensible multi-agent system.

The four-phase design process maps directly to Python implementation with no design decisions left unaccounted for.

---

**All 19 functionalities implemented**
**All 3 scenarios verified**
**Controlled substance policy enforced**
**Proactive escalation every cycle**
**FEFO batch expiry tracking**

---

*DCIT 403 — Intelligent Agent Systems*
*Student ID: 11126586*

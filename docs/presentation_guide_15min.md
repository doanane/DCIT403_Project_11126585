# MedStock Presentation Guide and 15-Minute Pitch Script

Student ID: 11126586  
Course: DCIT 403 - Intelligent Agent Systems  
Methodology: Prometheus

---

## 1. What This Project Is (Simple Version)

MedStock is a hospital pharmacy decision-support simulator built with a multi-agent system.

It solves one main problem:
Hospitals lose time and patient safety when drugs run low, transfers are not coordinated, procurements are delayed, and expiry is not monitored.

The system therefore does four practical jobs:
1. Detect low stock quickly.
2. Decide if a ward can be helped by internal transfer or external procurement.
3. Escalate delayed procurement orders automatically.
4. Track expiry dates and enforce FEFO (First Expired, First Out) so near-expiry drugs are used first.

---

## 2. End-to-End Runtime Flow

This is the exact flow when you run `main.py`:

1. `main.py` creates `MedStockApp` and starts Tkinter.
2. `MedStockApp` creates `MedStockSimulator`.
3. `MedStockSimulator` initializes:
   - Drug database
   - Ward database
   - Supplier database
   - Initial stock values
   - Five agents
   - Sensor schedule
   - Expiry-tracked batches
4. Each simulation step:
   - Sensor emits scheduled stock readings.
   - Agents run in this order:
     1) StockMonitorAgent
     2) SupplyAssessmentAgent
     3) TransferCoordinationAgent
     4) ExpiryMonitorAgent
     5) ProcurementEscalationAgent
5. UI refreshes all panels from latest data.

Why order matters:
Expiry alerts are produced by `ExpiryMonitorAgent` and then immediately consumed by `ProcurementEscalationAgent` in the same step.

---

## 3. What Each File/Component Means

## 3.1 Entry Point and UI Shell

File: `main.py`  
Meaning: Application bootstrap. It only launches the Tkinter app.

File: `ui/app.py`  
Meaning: Complete presentation layer. It contains:
- Control buttons (Step, Auto Run, Reset)
- Manual input controls
- Data tables
- Logs
- Refresh logic

File: `ui/theme.py`  
Meaning: Centralized visual style tokens (colors and fonts), including expiry colors.

---

## 3.2 Core Agent Framework

File: `src/core/message.py`  
Meaning: Shared message contract between agents.

`Performative` enum meanings:
- `STOCK_READING`: sensor or manual stock event.
- `STOCK_ALERT`: low stock warning from stock monitor.
- `SHORTAGE_CLASSIFIED`: assessed shortage with strategy metadata.
- `TRANSFER_RESULT`: transfer outcome (success/failure).
- `PROCUREMENT_REQUEST`: procurement intent (defined for protocol completeness).
- `ESCALATION_NOTICE`: escalation signal (defined for protocol completeness).
- `STATUS_UPDATE`: generic status message (defined for extensibility).
- `EXPIRY_ALERT`: near-expiry/expired escalation message.

`Message` dataclass meaning:
- `performative`: intent type.
- `sender`: who sent it.
- `recipient`: target agent.
- `content`: business payload.

File: `src/core/agent.py`  
Meaning: Abstract agent lifecycle engine.

Key methods:
- `receive`: push message into inbox queue.
- `send`: deliver message through `AgentSystem`.
- `run_cycle`: process inbox then execute proactive logic.
- `handle_message`: per-agent reactive logic (override in subclasses).
- `proactive_step`: per-agent proactive logic (override in subclasses).

File: `src/core/agent_system.py`  
Meaning: In-memory message router.

Key methods:
- `register`: map agent name to instance.
- `deliver`: route message to recipient inbox.

---

## 3.3 Environment

File: `src/environment/pharmacy_sensor.py`  
Meaning: Source of percepts/events in this simulation.

Key logic:
- `schedule_reading(step, drug, ward, qty)`: preload event timeline.
- `emit(current_step)`: send `STOCK_READING` messages for matching step.

---

## 3.4 Belief/Data Layer

File: `src/beliefs/drug_belief.py`  
Meaning: Drug, stock, and batch-expiry state.

Enums:
- `DrugCategory`: CONTROLLED, ESSENTIAL, STANDARD.
- `SeverityLevel`: CRITICAL, HIGH, MEDIUM, LOW, OK.
- `ExpiryStatus`: EXPIRED, EXPIRING_SOON, WARNING, OK.

Data classes:
- `Drug`: static master data (name, unit, threshold).
- `StockRecord`: stock at `(drug, ward)` and dynamic severity calculation.
- `ExpiryBatch`: one lot with its expiry step.

`DrugDatabase` key meanings:
- `_drugs`: dictionary of drug metadata.
- `_stocks`: dictionary of live stock records.
- `_batches`: dictionary of batch-level expiry records.
- `set_stock`: updates stock and also keeps batch model consistent.
- `_consume_batches_fefo`: if stock decreases, consume earliest-expiring batches first.
- `_register_restock_batch`: if stock increases, create a new long-dated batch.

File: `src/beliefs/ward_belief.py`  
Meaning: Ward directory and transfer history.

- `Ward`: ward identity and priority.
- `TransferRecord`: auditable transfer event.
- `WardDatabase`: create/get transfer records and wards.

File: `src/beliefs/supplier_belief.py`  
Meaning: Supplier registry and procurement history.

- `Supplier`: supplier capability and lead time.
- `ProcurementRecord`: lifecycle of each procurement order.
- `SupplierDatabase`: supplier lookup and procurement creation.

---

## 3.5 Agent Layer (Business Intelligence)

### StockMonitorAgent
File: `src/agents/stock_monitor_agent.py`

What it means:
- Receives `STOCK_READING`.
- Updates stock in `DrugDatabase`.
- Calculates severity by threshold ratio.
- Sends one `STOCK_ALERT` per `(drug, ward)` for MEDIUM/HIGH/CRITICAL states.

Why it exists:
- Decouples sensing from decision and keeps duplicate alerts under control.

### SupplyAssessmentAgent
File: `src/agents/supply_assessment_agent.py`

What it means:
- Receives `STOCK_ALERT`.
- Builds shortage object and classifies response plan.

Decision policy:
- CRITICAL -> send to Transfer AND Procurement (procurement waits for transfer result).
- HIGH -> transfer-first.
- MEDIUM -> procurement-only.

Why it exists:
- Converts raw low-stock alerts into policy-driven action plans.

### TransferCoordinationAgent
File: `src/agents/transfer_coordination_agent.py`

What it means:
- Handles `SHORTAGE_CLASSIFIED`.
- Rejects controlled substances for internal transfer.
- Finds donor ward with usable surplus.
- Executes stock move and records transfer.
- Sends `TRANSFER_RESULT` to procurement agent.

Why it exists:
- Enables rapid intra-hospital balancing before external procurement.

### ProcurementEscalationAgent
File: `src/agents/procurement_escalation_agent.py`

What it means:
- Handles shortage classification, transfer outcomes, and expiry alerts.
- Creates procurement orders when needed.
- Runs proactive escalation timer every cycle.
- Tracks resolved shortages and expiry escalations.

Important parameter:
- `ESCALATION_TIMEOUT_STEPS = 5`

Why it exists:
- Makes procurement dependable and prevents silent delays.

### ExpiryMonitorAgent
File: `src/agents/expiry_monitor_agent.py`

What it means:
- Proactively scans all batches each step.
- Classifies batch status by remaining steps.
- Logs FEFO ordering guidance.
- Sends `EXPIRY_ALERT` for EXPIRED or EXPIRING_SOON batches.

Important parameters:
- `EXPIRING_SOON_THRESHOLD = 3`
- `WARNING_THRESHOLD = 6`

Why it exists:
- Adds medicine safety and waste reduction to the supply intelligence loop.

---

## 3.6 Simulation Orchestration

File: `src/simulation/simulator.py`

What it means:
- Creates the full environment and all agents.
- Seeds initial stock and scenario events.
- Seeds expiry batches from all stocks (two lots per stock record).
- Runs one deterministic step at a time.

Key preloaded scenario events:
- Step 1: Insulin in ICU (critical)
- Step 3: Morphine in Surgical (high, controlled transfer denied)
- Step 8: Amoxicillin in Surgical (high)
- Step 10: Paracetamol in General (medium)
- Step 14: Simulated supplier confirmation for `paracetamol_GENERAL`

---

## 4. Decision Logic You Should Explain Clearly

### 4.1 Stock Severity Formula

`ratio = current_stock / reorder_threshold`

Thresholds:
- `< 0.10` => CRITICAL
- `< 0.30` => HIGH
- `< 0.50` => MEDIUM
- `< 0.75` => LOW
- `>= 0.75` => OK

### 4.2 Controlled Substance Rule

If drug category is CONTROLLED, transfer is denied immediately.
Reason: safety and policy compliance.
Fallback: procurement path.

### 4.3 Escalation Rule

Any procurement still REQUESTED after 5 simulation steps becomes ESCALATED.

### 4.4 Expiry Classification Rule

`steps_remaining = expiry_step - current_step`

- `<= 0` => EXPIRED
- `<= 3` => EXPIRING_SOON
- `<= 6` => WARNING
- `> 6` => OK

### 4.5 FEFO Rule

When stock decreases, consumption is applied to earliest-expiring batches first.
This is implemented in the database layer, not only logged.

---

## 5. UI Walkthrough (What Each Tab/Section Does)

The app has one window with multiple sections.

## 5.1 Header Controls

- `Step`: advance exactly one simulation step.
- `Auto Run`: run repeatedly until paused or finished.
- `Speed (s/step)`: delay between auto steps.
- `Reset`: clear and rebuild simulation from step 0.

What to say:
"These controls let me either run deterministic single-step analysis or a continuous run for full scenario playback."

## 5.2 Manual Stock Input Row

- Drug dropdown
- Ward dropdown
- Quantity input
- Submit Reading button

What it does:
Injects a `STOCK_READING` event manually and immediately runs all agents for current step.

What to say:
"This is my interactive testing harness. I can force new scenarios without editing code."

## 5.3 Drug Stock Levels Panel

Columns:
- Drug, Category, Ward, Stock, Threshold, Level%, Status

Behavior:
- Rows are color-coded by severity.
- Sortable columns.

What to say:
"This is my real-time inventory state table and severity heatmap."

## 5.4 Active Alerts Panel

Columns:
- ID, Drug, Ward, Severity, Category, Step Detected, Status

Behavior:
- Shows shortage states from active/resolved/procurement contexts.

What to say:
"This panel shows the lifecycle of shortage alerts from detection to resolution or escalation."

## 5.5 Operations Notebook Tab 1: Transfers

Columns:
- Transfer ID, Drug, From Ward, To Ward, Qty, Status, Step

Behavior:
- Tracks successful and failed transfer attempts.

What to say:
"This tab proves whether transfer-first policy is working before procurement is initiated."

## 5.6 Operations Notebook Tab 2: Procurement

Columns:
- Record ID, Drug, Supplier, Qty, Status, Step, Escalated

Behavior:
- Shows requested, escalated, and confirmed orders.

What to say:
"This tab is the procurement audit trail and SLA monitor."

## 5.7 Operations Notebook Tab 3: Expiry Monitor

Columns:
- Batch ID, Drug, Ward, Qty, Exp Step, Status, Detected

Behavior:
- Shows warning/expiring/expired batches.
- Sorted by urgency.

What to say:
"This tab demonstrates expiry intelligence and batch-level visibility, not just aggregate stock numbers."

## 5.8 Activity Log Panel

Behavior:
- Shows step separators and per-agent logs.
- Color-coded by agent category.

What to say:
"This is my explainability layer. Every decision in the multi-agent chain is visible."

## 5.9 Status Bar

Shows:
- Step progress
- Alert count
- Transfer count
- Procurement count
- Expiry alert count
- Run state

What to say:
"This gives a one-line operational summary for quick monitoring."

---

## 6. Thorough Demo Steps (Recommended Live Sequence)

1. Start app with `python main.py`.
2. Explain header controls first.
3. Point at stock table and highlight color coding.
4. Click `Step` to run step 1.
5. Show logs for Insulin ICU critical detection.
6. Open Transfers tab and show transfer created.
7. Open Active Alerts and explain status movement.
8. Step to 3 and show Morphine controlled-transfer denial.
9. Open Procurement tab and show procurement creation.
10. Continue to step 8 and show escalation of pending procurement.
11. Step to 10 and show medium shortage procurement path.
12. Step to 14 and show supplier confirmation event.
13. Open Expiry Monitor tab and explain warning/expiring/expired states.
14. Use manual stock input to inject a new reading and show real-time reaction.
15. End with status bar summary and architectural recap.

---

## 7. 15-Minute Word-for-Word Pitch Script

Use this exactly as spoken text. You can read it directly.

### 00:00 - 01:00 (Opening)
"Good [morning/afternoon]. My name is [your name], student ID 11126586. I am presenting MedStock, a multi-agent hospital pharmacy intelligence system developed for DCIT 403 using the Prometheus methodology. The goal of this project is to reduce stock-out risk, coordinate emergency resupply quickly, and now also prevent medicine wastage and safety risk through expiry monitoring and FEFO usage. In simple terms, the system continuously checks stock levels across five wards, classifies shortages, tries internal transfer when appropriate, procures from suppliers when needed, escalates delayed procurement, and tracks expiry so near-expiry drugs are used first."

### 01:00 - 02:00 (Problem and Value)
"Hospitals often have three linked problems: one ward is understocked while another has surplus, procurement follow-up is inconsistent, and expiry management is weak at batch level. MedStock addresses all three in one coordinated architecture. It is not just a dashboard. It is an agent system where each agent has a specific responsibility and communicates through typed messages. This gives modularity, traceability, and policy control. The output is operationally useful because each decision, from shortage detection to transfer or escalation, is visible in logs and records."

### 02:00 - 03:00 (Architecture Overview)
"Architecturally, there are five intelligent agents. StockMonitorAgent receives stock readings and detects shortage severity. SupplyAssessmentAgent decides response strategy based on severity and category. TransferCoordinationAgent attempts intra-hospital redistribution and enforces controlled drug policy. ProcurementEscalationAgent creates supplier requests and escalates overdue requests. ExpiryMonitorAgent scans all batches for expiry risk and raises expiry alerts. Communication uses a central message-passing core with performatives like STOCK_ALERT, SHORTAGE_CLASSIFIED, TRANSFER_RESULT, and EXPIRY_ALERT."

### 03:00 - 04:00 (Execution Flow)
"At startup, the simulator initializes drugs, wards, suppliers, initial stocks, sensor events, agents, and expiry-tracked batches. Then each step runs in deterministic order: stock monitor, assessment, transfer, expiry monitor, then procurement and escalation. This order is important because expiry alerts generated by ExpiryMonitorAgent can be consumed by ProcurementEscalationAgent in the same step. The simulation is deterministic and repeatable, which is useful for demonstration and testing."

### 04:00 - 05:00 (Core Decision Rules)
"The stock severity formula is ratio-based: current stock divided by reorder threshold. Less than ten percent is critical, less than thirty percent is high, less than fifty percent is medium. Controlled substances, such as morphine, are not transferable internally by policy, so transfer is denied and procurement is triggered. Procurement escalation uses a five-step timeout: any unconfirmed request is escalated automatically. Expiry classification uses steps remaining: expired at zero or below, expiring soon within three steps, warning within six steps."

### 05:00 - 06:00 (FEFO Logic)
"A key enhancement is FEFO, First Expired, First Out. I implemented FEFO in the data model itself, not only as a log recommendation. When stock decreases, the system consumes earliest-expiring batches first. This means stock movement is physically consistent with expiry policy. If stock increases, the system registers a new long-dated replenishment batch. This creates realistic batch behavior and improves both safety and wastage control."

### 06:00 - 07:00 (UI Orientation)
"Now I will walk through the interface. At the top I have execution controls: single-step, auto-run, speed, and reset. Below that is manual stock input for interactive scenario injection. The left upper panel is Drug Stock Levels with status color coding and sortable columns. The right upper panel is Active Alerts, showing shortage lifecycle and current status. The lower-left region is Operations with three tabs: Transfers, Procurement, and Expiry Monitor. The lower-right region is Activity Log, and the footer is a compact status bar summary."

### 07:00 - 08:00 (Step 1 Demo)
"I run step one. The sensor sends a critical insulin reading for ICU. StockMonitorAgent detects severe shortage and raises alert. SupplyAssessmentAgent classifies critical and sends to both transfer and procurement paths, but with transfer-first synchronization. TransferCoordinationAgent finds donor stock in another ward and completes transfer. ProcurementEscalationAgent receives transfer success and marks shortage resolved without unnecessary procurement. This demonstrates cost-conscious and fast response behavior."

### 08:00 - 09:00 (Step 3 Demo)
"Now I move to step three where morphine in Surgical is high shortage. Because morphine is controlled, transfer is denied immediately by policy. That failure result is sent to procurement, and procurement request is created. This shows policy compliance: the system does not break controlled-drug handling rules even under shortage pressure. I can verify this in the Transfers tab as FAILED, in Procurement as REQUESTED, and in the log as a traceable chain of decisions."

### 09:00 - 10:00 (Escalation Demo)
"I continue to step eight. Since the morphine procurement has remained requested for five steps, ProcurementEscalationAgent escalates it automatically. This is proactive behavior, not passive waiting. Also at step eight, amoxicillin shortage in Surgical appears and transfer coordination can succeed where policy allows. So in one timeline, we see both outcomes: transfer denial for controlled drugs and transfer success for non-controlled drugs. This validates category-aware behavior."

### 10:00 - 11:00 (Medium Case and Confirmation)
"At step ten, paracetamol in General is medium severity. The classification policy for medium is procurement-only, so it bypasses transfer and creates a procurement request directly. At step fourteen, supplier confirmation is simulated and the procurement status changes to confirmed. This demonstrates end-to-end order lifecycle: requested, optionally escalated, then confirmed when supplier responds."

### 11:00 - 12:00 (Expiry Tab Demo)
"Now I open the Expiry Monitor tab. Here each row is a batch with batch ID, ward, quantity, expiry step, and current status. Warning, expiring soon, and expired states are prioritized and color-coded. The ExpiryMonitorAgent scans all batches every simulation step and sends EXPIRY_ALERT messages for urgent cases. These alerts are also captured by ProcurementEscalationAgent in an expiry escalation registry. So expiry is integrated into the same operational intelligence pipeline."

### 12:00 - 13:00 (Explainability and Robustness)
"A major strength of this design is explainability. Every action is logged by responsible agent, so I can trace why a transfer happened, why a procurement escalated, or why expiry alert was raised. Duplicate suppression is implemented to avoid noisy repeated events. The architecture is modular: agent responsibilities are separated, but coordination is done through explicit message contracts. This improves maintainability and makes policy changes easy to localize."

### 13:00 - 14:00 (Prometheus Mapping)
"From a Prometheus perspective, this project is complete across phases. System specification defines scenarios and goals. Architectural design defines agent roles and interactions. Interaction design is implemented through performatives and message payloads. Detailed design appears in each agent plan method and database belief structure. Reporting and rationale are documented in the project docs. So this is not just coding output; it is methodology-aligned agent engineering."

### 14:00 - 15:00 (Closing)
"In conclusion, MedStock demonstrates a practical hospital pharmacy multi-agent workflow with shortage intelligence, transfer coordination, procurement escalation, and expiry-aware FEFO enforcement. The project shows deterministic simulation, transparent decision traces, and a UI that supports both monitoring and interactive testing. Future extensions can include real-time sensor integration, demand forecasting, and automated quarantine for expired stock. Thank you. I am ready for questions on architecture, policy logic, and implementation details."

---

## 8. Quick Q and A Prep (High Probability Questions)

Q: Why use multi-agent instead of one large module?  
A: Separation of concerns, clearer policy boundaries, easier testing, and clearer audit trails.

Q: How do you prevent repeated alerts?  
A: Stock monitor tracks alerted `(drug, ward)` pairs; assessment tracks active shortages; procurement ignores duplicate shortage and duplicate expiry state updates.

Q: How is safety handled for controlled drugs?  
A: Transfer agent enforces hard deny for `DrugCategory.CONTROLLED`, forcing procurement path.

Q: Where is FEFO really enforced?  
A: In `DrugDatabase.set_stock`, through `_consume_batches_fefo`, so earliest-expiring batch is consumed first during stock reduction.

Q: What makes escalation proactive?  
A: Procurement agent runs escalation check every cycle even without incoming messages.

Q: What is one limitation?  
A: It is currently simulation-driven with deterministic events, not yet connected to live hospital systems.

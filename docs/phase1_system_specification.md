# Phase 1 - System Specification
## MedStock: Hospital Pharmacy Stock Depletion and Emergency Resupply Coordination

**Student ID:** 11126586
**Course:** DCIT 403 - Intelligent Agent Systems
**Methodology:** Prometheus (Padgham and Winikoff, 2004)

---

## 1. Problem Description

### What problem are we solving?

Hospital pharmacies in Ghana and across the developing world face a persistent and often life-threatening operational failure: critical drug stock depletion goes undetected until a nurse or doctor physically discovers an empty shelf during an emergency. By that point, a patient in the ICU may need insulin that the ward ran out of two days ago. The problem is not necessarily one of procurement failure but of information failure. Pharmacy managers rely on manual stock-take processes, handwritten ledgers, and periodic reports that may be hours or days out of date. No mechanism exists to automatically detect a stock fall, assess whether a nearby ward can donate surplus supply, initiate an emergency procurement order, and escalate to hospital administration if the supplier does not confirm delivery.

MedStock addresses this gap by deploying four coordinated intelligent agents that continuously monitor drug stock levels across all wards, classify shortages by clinical severity and drug category, coordinate internal ward transfers when surplus exists, and initiate and track external procurement requests. The system acts without waiting for human observation, producing a faster and more reliable supply chain than any manual process can achieve.

### Why is an agent-based approach appropriate?

An agent-based approach is appropriate for this domain for the following reasons drawn from Padgham and Winikoff (2004):

**Reactivity:** Drug stock levels change continuously as patients consume medication. Sensor readings arrive asynchronously from multiple wards. Each StockMonitorAgent reading requires an immediate comparison against the reorder threshold and an immediate decision about whether to alert the downstream assessment pipeline. A reactive architecture handles this far better than any scheduled batch job.

**Proactivity:** The ProcurementEscalationAgent does not wait to be asked whether an order has been confirmed. Every simulation cycle it proactively inspects all pending procurement records and compares the elapsed steps against the escalation timeout. If a supplier has not confirmed within five steps, the agent escalates the procurement to hospital administration without any external trigger. This goal-directed initiative is a defining characteristic of intelligent agents.

**Social ability:** The four agents divide the supply chain problem along functional lines that mirror real hospital departments: pharmacy surveillance, clinical assessment, logistics coordination, and procurement management. They communicate exclusively through structured messages, allowing each agent to operate independently while forming a coherent coordinated pipeline. A single monolithic program cannot achieve this separation of concerns.

**Situatedness:** The agents perceive drug stock readings from the environment (the PharmacySensor), act upon that environment by updating ward stock levels in the shared database after a transfer, and send messages that trigger supplier actions in the external world. The system is embedded in the hospital operational environment rather than operating in isolation.

### Stakeholders

| Stakeholder | Role in the system |
|---|---|
| ICU Pharmacist | Needs immediate notification of critical stock depletion for life-sustaining medications |
| Ward Nurses | Depend on reliable drug availability; benefit from automatic resupply coordination |
| Hospital Administrator | Receives escalation notices when procurement is overdue |
| Procurement Officer | Receives automated procurement requests and confirms supplier deliveries |
| Suppliers (MedPharm, PharmaControl, BasicMeds) | Receive structured resupply orders and confirm or delay fulfilment |
| Drug Regulatory Authority | Requires that controlled substances (morphine) are never transferred between wards without regulatory clearance |

---

## 2. Goal Specification

### Top-Level Goal

Ensure continuous availability of critical pharmaceutical supplies across all hospital wards by automatically detecting shortages, coordinating transfers, initiating procurement, and escalating overdue orders.

### Sub-Goals

**G1 - Monitor drug stock levels across all wards**
- G1.1: Receive stock readings from the pharmacy sensor network
- G1.2: Compute stock level as a percentage of the reorder threshold
- G1.3: Classify each reading by severity (CRITICAL, HIGH, MEDIUM, LOW, OK)
- G1.4: Suppress duplicate alerts for the same drug-ward combination

**G2 - Classify shortages by clinical priority and regulatory context**
- G2.1: Map each shortage to its drug category (CONTROLLED, ESSENTIAL, STANDARD)
- G2.2: Select the appropriate response plan based on severity
- G2.3: Prevent duplicate processing of the same shortage record
- G2.4: Track all active shortages with full metadata

**G3 - Coordinate internal ward transfers for non-controlled drugs**
- G3.1: Search all wards for a donor ward with sufficient surplus
- G3.2: Calculate safe transfer quantity that does not deplete the donor ward
- G3.3: Update both ward stock levels after a successful transfer
- G3.4: Record every transfer attempt with full audit trail
- G3.5: Enforce the regulatory policy that controlled substances cannot be transferred internally

**G4 - Initiate emergency procurement from approved suppliers**
- G4.1: Select the appropriate supplier based on drug category
- G4.2: Create a procurement record with full drug, ward, and quantity details
- G4.3: Track procurement status (REQUESTED, CONFIRMED, ESCALATED)
- G4.4: Await supplier confirmation events

**G5 - Escalate overdue procurement orders**
- G5.1: Proactively check elapsed steps for every pending procurement
- G5.2: Mark procurement as ESCALATED when timeout is exceeded
- G5.3: Notify hospital administration of the escalation

---

## 3. Functionalities

| ID | Functionality |
|---|---|
| F1 | Receive drug stock readings from the pharmacy sensor network per simulation step |
| F2 | Compute stock level percentage relative to reorder threshold |
| F3 | Classify stock level by severity: CRITICAL (below 10%), HIGH (10-30%), MEDIUM (30-50%) |
| F4 | Suppress duplicate alerts for stock-ward pairs already alerted in this simulation |
| F5 | Classify shortage by drug category and select the appropriate response plan |
| F6 | Route CRITICAL shortages to both transfer and procurement agents simultaneously |
| F7 | Route HIGH shortages to transfer coordination only (transfer-first policy) |
| F8 | Route MEDIUM shortages to procurement watching only |
| F9 | Enforce controlled substance policy (no internal transfer of morphine or other CONTROLLED drugs) |
| F10 | Search all wards for a surplus donor ward meeting surplus ratio and quantity criteria |
| F11 | Execute inter-ward stock transfer and update both ward records |
| F12 | Record every transfer attempt (successful or failed) with full audit trail |
| F13 | Select supplier by drug category from the supplier registry |
| F14 | Create procurement record and notify procurement pipeline |
| F15 | Proactively monitor pending procurements every cycle for timeout |
| F16 | Escalate overdue procurement to ESCALATED status after five steps |
| F17 | Receive and process supplier confirmation events |
| F18 | Track resolved shortages to avoid reprocessing |
| F19 | Provide a full audit trail of all transfers and procurements via the simulation log |

---

## 4. Scenarios

### Scenario 1: Critical Insulin Shortage in the ICU (Transfer Success)

At the start of the simulation, the pharmacy sensor network reports that the ICU ward has only 8 units of Insulin remaining against a reorder threshold of 100 units. This represents 8% of the threshold, which the StockMonitorAgent classifies as CRITICAL. The agent immediately sends a STOCK_ALERT to the SupplyAssessmentAgent.

The SupplyAssessmentAgent classifies the shortage as CRITICAL with category ESSENTIAL. Following the CRITICAL plan, it sends a SHORTAGE_CLASSIFIED message to both the TransferCoordinationAgent and the ProcurementEscalationAgent simultaneously. The message to the ProcurementEscalationAgent includes the flag await_transfer_result=True, instructing it to hold off on procurement until the transfer outcome is known.

The TransferCoordinationAgent searches all wards for a donor. It finds that the EMERGENCY ward holds 120 units of Insulin, giving a surplus ratio of 1.2, which exceeds the 0.5 threshold. It transfers 60 units from EMERGENCY to ICU, updates both ward stock levels, and sends a TRANSFER_RESULT(success=True) to the ProcurementEscalationAgent. On receiving the success message, the ProcurementEscalationAgent marks the shortage as resolved without initiating any procurement. The ICU shortage is resolved at step 1.

### Scenario 2: Morphine CRITICAL Shortage in Surgical Ward (Controlled Substance Escalation)

At step 3, the sensor network reports 7 mg of Morphine remaining in the Surgical Ward against a threshold of 50 mg (14% of threshold). This falls in the HIGH severity band. The StockMonitorAgent sends a STOCK_ALERT to the SupplyAssessmentAgent, which classifies the shortage as HIGH with category CONTROLLED. The HIGH plan routes the shortage to the TransferCoordinationAgent only.

The TransferCoordinationAgent recognises that Morphine is a CONTROLLED drug. Regulatory policy prohibits internal transfer of controlled substances between wards. It immediately sends TRANSFER_RESULT(success=False, reason=controlled_substance_policy) to the ProcurementEscalationAgent.

On receiving the failed transfer, the ProcurementEscalationAgent initiates procurement from PharmaControl Ltd, the designated controlled-substance supplier, creating procurement record PR-001. Because no supplier confirmation arrives, the ProcurementEscalationAgent escalates the procurement at step 8, five steps after it was dispatched. The shortage status becomes ESCALATED.

### Scenario 3: Multi-Drug Shortage (Transfer Success and Procurement Confirmation)

At step 8, Amoxicillin in the Surgical Ward is reported at 40 tablets against a threshold of 200 tablets (20%, HIGH severity). The SupplyAssessmentAgent routes this to the TransferCoordinationAgent, which finds the ICU ward holds 150 tablets with a surplus ratio of 0.75. A transfer of 75 tablets is completed (TR-003), resolving the shortage.

At step 10, Paracetamol in the General Ward is reported at 160 tablets against a threshold of 500 tablets (32%, MEDIUM severity). The SupplyAssessmentAgent routes this directly to the ProcurementEscalationAgent, which creates procurement record PR-002 with BasicMeds Supplies. At step 14, a supplier confirmation event arrives and PR-002 is marked CONFIRMED, demonstrating the full procurement confirmation cycle.

---

## 5. Environment Description

### What environment does the agent system operate in?

The MedStock system operates in a hospital pharmacy environment modelled as a network of five wards (ICU, EMERGENCY, SURGICAL, MATERNITY, GENERAL), each holding stock of five drugs. The environment includes:

- A sensor network (PharmacySensor) that emits stock readings at scheduled steps
- A shared drug stock database reflecting current stock levels in each ward
- A supplier registry with three approved suppliers
- A regulatory policy that prevents internal transfer of controlled substances

The environment is:
- **Partially observable:** Agents see only the stocks and events the sensor emits. Wards with no sensor events remain at their initial stock levels.
- **Dynamic:** Stock levels change when transfers are executed. The sensor network emits new readings at scheduled steps.
- **Event-driven and discrete:** The simulation advances in steps. Sensor events, transfer results, and supplier confirmations are the key events.

### What do agents perceive?

| Percept | Description | Received by |
|---|---|---|
| STOCK_READING | Drug ID, ward ID, quantity, step from PharmacySensor | StockMonitorAgent |
| STOCK_ALERT | Drug, ward, severity, quantity needed, step | SupplyAssessmentAgent |
| SHORTAGE_CLASSIFIED | Full shortage record with severity, category, drug, ward | TransferCoordinationAgent, ProcurementEscalationAgent |
| TRANSFER_RESULT | Success flag, shortage ID, reason, transfer details | ProcurementEscalationAgent |

### What can agents act upon?

| Action | Agent | Description |
|---|---|---|
| Set stock level | StockMonitorAgent | Updates DrugDatabase with new sensor reading |
| Send STOCK_ALERT | StockMonitorAgent | Notifies SupplyAssessmentAgent of detected shortage |
| Register active shortage | SupplyAssessmentAgent | Stores shortage record in active_shortages dict |
| Send SHORTAGE_CLASSIFIED | SupplyAssessmentAgent | Routes shortage to correct downstream agents |
| Update ward stock | TransferCoordinationAgent | Modifies both donor and recipient stock after transfer |
| Create transfer record | TransferCoordinationAgent | Writes TransferRecord to WardDatabase |
| Send TRANSFER_RESULT | TransferCoordinationAgent | Notifies ProcurementEscalationAgent of outcome |
| Create procurement record | ProcurementEscalationAgent | Writes ProcurementRecord to SupplierDatabase |
| Escalate procurement | ProcurementEscalationAgent | Changes status to ESCALATED in procurement record |
| Mark shortage resolved | ProcurementEscalationAgent | Moves shortage from active to resolved_shortages |

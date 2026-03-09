# Phase 2 - Architectural Design
## MedStock: Hospital Pharmacy Stock Depletion and Emergency Resupply Coordination

**Student ID:** 11126586
**Course:** DCIT 403 - Intelligent Agent Systems
**Methodology:** Prometheus (Padgham and Winikoff, 2004)

---

## 1. Agent Types

The MedStock system contains four agent types. The division of responsibility follows functional lines derived from real hospital pharmacy operations.

### 1.1 StockMonitorAgent

This agent is the entry point for all environmental data. It receives STOCK_READING messages from the PharmacySensor environment object and performs the first level of reasoning: is this stock level alarming enough to require a response? It computes the stock percentage relative to the reorder threshold, classifies the severity, and sends STOCK_ALERT messages downstream. It maintains an alerted_stocks set so that a stock level already flagged once does not generate repeated alerts even if the sensor continues to report the same low value.

**Justification:** A dedicated monitoring agent is appropriate because monitoring is a continuous, reactive task that must be separated from the higher-level classification and decision-making work. Combining monitoring with assessment would create a single point of responsibility for too many concerns.

### 1.2 SupplyAssessmentAgent

This agent receives STOCK_ALERT messages and makes the central classification and routing decision. It determines the drug category (CONTROLLED, ESSENTIAL, STANDARD) and uses the severity level to select among three alternative plans: the CRITICAL plan (parallel transfer and procurement), the HIGH plan (transfer-first), and the MEDIUM plan (procurement watch). This agent is responsible for ensuring that each unique shortage is classified only once.

**Justification:** A dedicated assessment agent is needed because the routing logic is non-trivial and depends on both severity and drug category. Embedding this logic in the monitoring agent or the transfer agent would obscure the decision-making process and make the system harder to extend.

### 1.3 TransferCoordinationAgent

This agent receives SHORTAGE_CLASSIFIED messages and attempts to resolve the shortage through an internal inter-ward transfer. It enforces the controlled substance policy, searches for a suitable donor ward, executes the transfer by updating both ward stock levels, and sends a TRANSFER_RESULT message to inform the ProcurementEscalationAgent of the outcome. All transfer attempts are recorded in the WardDatabase for full auditability.

**Justification:** Transfer coordination involves database operations on ward stock levels and requires awareness of both the shortage ward and all potential donor wards. Separating this from procurement allows the two resolution strategies to operate independently.

### 1.4 ProcurementEscalationAgent

This agent manages the full procurement lifecycle. It receives SHORTAGE_CLASSIFIED messages for MEDIUM cases (direct procurement) and TRANSFER_RESULT messages to know when procurement is needed following a failed transfer. It creates procurement records, tracks them step by step, proactively checks for timeout, and escalates overdue orders. It also handles supplier confirmation events injected by the simulator.

**Justification:** Procurement involves temporal reasoning (how many steps have elapsed since dispatch?) that no other agent performs. This proactive, step-aware behaviour is distinct enough to warrant a dedicated agent.

---

## 2. Functionality-to-Agent Mapping

| Functionality | Agent |
|---|---|
| F1, F2, F3, F4: Monitor and classify stock readings | StockMonitorAgent |
| F5, F6, F7, F8: Classify shortage and select response plan | SupplyAssessmentAgent |
| F9, F10, F11, F12: Transfer coordination and controlled substance policy | TransferCoordinationAgent |
| F13, F14, F17, F18: Supplier selection and procurement creation | ProcurementEscalationAgent |
| F15, F16: Proactive escalation monitoring | ProcurementEscalationAgent |
| F19: Audit trail | All agents via log_callback |

---

## 3. Acquaintance Diagram

```
+---------------------+
|  PharmacySensor     |
|  (Environment)      |
+---------------------+
          |
          | STOCK_READING
          v
+---------------------+
|  StockMonitorAgent  |
+---------------------+
          |
          | STOCK_ALERT
          v
+----------------------+
|  SupplyAssessment    |
|       Agent          |
+----------------------+
       |          |
       |          |
       | SHORTAGE | SHORTAGE
       | CLASSIFIED| CLASSIFIED
       |           |
       v           v
+------------+ +--------------------+
| Transfer   | | Procurement        |
| Coord.     | | Escalation         |
| Agent      | | Agent              |
+------------+ +--------------------+
       |               ^
       | TRANSFER      |
       | RESULT        |
       +---------------+
```

Communication is strictly directional. No agent sends messages back to a higher-level agent except via TRANSFER_RESULT from TransferCoordinationAgent to ProcurementEscalationAgent.

---

## 4. Agent Descriptors

### StockMonitorAgent

| Attribute | Detail |
|---|---|
| Responsibilities | Monitor stock readings; compute severity; send alerts; suppress duplicates |
| Goals | G1.1, G1.2, G1.3, G1.4 |
| Beliefs | DrugDatabase (stock levels, thresholds, drug metadata); alerted_stocks set |
| Actions | set_stock(); send STOCK_ALERT |
| Interactions | Receives STOCK_READING from PharmacySensor; sends STOCK_ALERT to SupplyAssessmentAgent |

### SupplyAssessmentAgent

| Attribute | Detail |
|---|---|
| Responsibilities | Classify shortages by severity and category; select and execute response plan; prevent duplicate processing |
| Goals | G2.1, G2.2, G2.3, G2.4 |
| Beliefs | DrugDatabase (drug category); active_shortages dict keyed by shortage_id |
| Actions | Register shortage; send SHORTAGE_CLASSIFIED with plan-conditioned routing |
| Interactions | Receives STOCK_ALERT from StockMonitorAgent; sends SHORTAGE_CLASSIFIED to TransferCoordinationAgent and/or ProcurementEscalationAgent |

### TransferCoordinationAgent

| Attribute | Detail |
|---|---|
| Responsibilities | Enforce controlled substance policy; search for donor ward; execute transfer; record outcome |
| Goals | G3.1, G3.2, G3.3, G3.4, G3.5 |
| Beliefs | DrugDatabase (all ward stocks); WardDatabase (ward list, transfer records) |
| Actions | Update ward stocks; create_transfer(); send TRANSFER_RESULT |
| Interactions | Receives SHORTAGE_CLASSIFIED from SupplyAssessmentAgent; sends TRANSFER_RESULT to ProcurementEscalationAgent |

### ProcurementEscalationAgent

| Attribute | Detail |
|---|---|
| Responsibilities | Initiate procurement; track pending orders; proactively escalate overdue orders; confirm deliveries |
| Goals | G4.1, G4.2, G4.3, G4.4, G5.1, G5.2, G5.3 |
| Beliefs | SupplierDatabase; pending_procurements dict; resolved_shortages dict; _awaiting_transfer dict |
| Actions | create_procurement(); mark_escalated(); mark_resolved(); simulate_supplier_confirmation() |
| Interactions | Receives SHORTAGE_CLASSIFIED from SupplyAssessmentAgent; receives TRANSFER_RESULT from TransferCoordinationAgent; proactive_step() runs every cycle |

---

## 5. System Data Overview

| Data Store | Managed by | Contents |
|---|---|---|
| DrugDatabase | StockMonitorAgent, TransferCoordinationAgent | Drug metadata, all ward stock records |
| WardDatabase | TransferCoordinationAgent | Ward list, all TransferRecords |
| SupplierDatabase | ProcurementEscalationAgent | Supplier registry, all ProcurementRecords |
| active_shortages | SupplyAssessmentAgent | Dict of shortage_id to shortage info |
| pending_procurements | ProcurementEscalationAgent | Dict of shortage_id to procurement tracking |
| resolved_shortages | ProcurementEscalationAgent | Dict of shortage_id to resolution info |

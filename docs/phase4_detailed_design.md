# Phase 4 - Detailed Design
## MedStock: Hospital Pharmacy Stock Depletion and Emergency Resupply Coordination

**Student ID:** 11126586
**Course:** DCIT 403 - Intelligent Agent Systems
**Methodology:** Prometheus (Padgham and Winikoff, 2004)

---

## 1. Capabilities and Plans

### 1.1 StockMonitorAgent Capabilities

**Capability: MonitorStock**
- Percept: STOCK_READING message
- Plan: _plan_process_reading(content)
  1. Call drug_db.set_stock(drug_id, ward_id, quantity, step)
  2. Retrieve StockRecord and compute severity via record.severity()
  3. Log the reading with percentage level
  4. If severity is CRITICAL, HIGH, or MEDIUM:
     - Check if (drug_id, ward_id) is in alerted_stocks
     - If not: add to alerted_stocks, compute quantity_needed, send STOCK_ALERT
  5. If already alerted: no action (duplicate suppression)

**Context conditions for plan selection:** None. A single plan handles all severity levels with a conditional guard.

---

### 1.2 SupplyAssessmentAgent Capabilities

**Capability: ClassifyShortage**
- Percept: STOCK_ALERT message
- Plan: _plan_classify_shortage(content)
  1. Construct shortage_id = drug_id + "_" + ward_id
  2. Check active_shortages for duplicate; if present, return immediately
  3. Retrieve drug from DrugDatabase; extract category
  4. Build shortage_info dict; store in active_shortages[shortage_id]
  5. Select plan based on severity:

**Plan: CRITICAL_plan** (context: severity == CRITICAL)
- Send SHORTAGE_CLASSIFIED to TransferCoordinationAgent
- Send SHORTAGE_CLASSIFIED to ProcurementEscalationAgent with await_transfer_result=True

**Plan: HIGH_plan** (context: severity == HIGH)
- Send SHORTAGE_CLASSIFIED to TransferCoordinationAgent only

**Plan: MEDIUM_plan** (context: severity == MEDIUM)
- Send SHORTAGE_CLASSIFIED to ProcurementEscalationAgent only

---

### 1.3 TransferCoordinationAgent Capabilities

**Capability: CoordinateTransfer**
- Percept: SHORTAGE_CLASSIFIED message
- Plan: _plan_coordinate_transfer(content)
  1. Extract drug_id, ward_id, quantity_needed, category, step
  2. Retrieve drug from DrugDatabase
  3. Check drug.category:

**Plan: ControlledDenialPlan** (context: drug.category == DrugCategory.CONTROLLED)
- Log regulatory denial
- Create TransferRecord with status=FAILED, from_ward="N/A", quantity=0
- Send TRANSFER_RESULT(success=False, reason="controlled_substance_policy")

**Plan: TransferSearchPlan** (context: drug.category != CONTROLLED)
- Iterate all wards excluding shortage ward
- For each ward: get stock, compute surplus_ratio = current_stock / reorder_threshold
- Donor valid if surplus_ratio > 0.5 AND current_stock > quantity_needed * 0.5
- If no donor: create FAILED TransferRecord, send TRANSFER_RESULT(success=False)
- If donor found:
  - transfer_qty = min(quantity_needed, int(donor_stock * 0.5))
  - Update donor stock: donor_current - transfer_qty
  - Update recipient stock: recipient_current + transfer_qty
  - Create COMPLETED TransferRecord
  - Send TRANSFER_RESULT(success=True, transfer_id, transfer_qty, from_ward)

---

### 1.4 ProcurementEscalationAgent Capabilities

**Capability: HandleShortageClassified**
- Percept: SHORTAGE_CLASSIFIED message
- Plan: _plan_handle_shortage_classified(content)
  - If await_transfer_result=True: store in _awaiting_transfer dict, wait
  - If await_transfer_result=False (MEDIUM case): call _initiate_procurement(content)

**Capability: HandleTransferResult**
- Percept: TRANSFER_RESULT message
- Plan: _plan_handle_transfer_result(content)
  - If success=True: move shortage to resolved_shortages, delete from _awaiting_transfer
  - If success=False: pop from _awaiting_transfer if present, call _initiate_procurement(source_content)

**Capability: InitiateProcurement**
- Internal plan: _initiate_procurement(content)
  1. Check pending_procurements and resolved_shortages; if present, return (dedup)
  2. Extract drug_id, category (lowercase), quantity_needed
  3. Call supplier_db.find_supplier(category) to get matching supplier
  4. Call supplier_db.create_procurement() to create ProcurementRecord with status=REQUESTED
  5. Store in pending_procurements[shortage_id] with dispatch_step=current_step

**Capability: ProactiveEscalation**
- Triggered: proactive_step() every simulation cycle
- Plan: _plan_check_and_escalate()
  - For each pending procurement with status=REQUESTED:
    - Compute steps_elapsed = current_step - dispatch_step
    - If steps_elapsed >= ESCALATION_TIMEOUT_STEPS (5):
      - Update ProcurementRecord.status to ESCALATED
      - Set escalated_step = current_step
      - Log escalation

**Capability: ConfirmSupply**
- External trigger: simulate_supplier_confirmation(shortage_id, step)
- Plan: Find procurement in pending_procurements; if status=REQUESTED, set to CONFIRMED, set confirmed_step

---

## 2. Belief Structures

### drug_belief.py

- **DrugCategory (Enum):** CONTROLLED, ESSENTIAL, STANDARD
- **SeverityLevel (Enum):** CRITICAL, HIGH, MEDIUM, LOW, OK
- **Drug (dataclass):** drug_id, name, category, unit, reorder_threshold
- **StockRecord (dataclass):** drug_id, ward_id, current_stock, reorder_threshold, last_updated_step
  - severity() method: CRITICAL if ratio < 0.10; HIGH if < 0.30; MEDIUM if < 0.50; LOW if < 0.75; else OK
- **DrugDatabase:** add_drug(), set_stock(), get_stock(), get_all_stocks(), get_all_drugs()

### ward_belief.py

- **TransferStatus (Enum):** PENDING, COMPLETED, FAILED
- **Ward (dataclass):** ward_id, name, priority
- **TransferRecord (dataclass):** transfer_id, drug_id, drug_name, from_ward_id, to_ward_id, quantity, status, initiated_step, completed_step
- **WardDatabase:** add_ward(), create_transfer(), get_all_transfers()
  - transfer_id format: TR-001, TR-002, ...

### supplier_belief.py

- **ProcurementStatus (Enum):** REQUESTED, CONFIRMED, ESCALATED
- **Supplier (dataclass):** supplier_id, name, drug_categories (list of str), lead_time_steps
- **ProcurementRecord (dataclass):** record_id, drug_id, drug_name, ward_id, quantity_requested, supplier_id, supplier_name, status, requested_step, confirmed_step, escalated_step, is_controlled
- **SupplierDatabase:** add_supplier(), find_supplier(drug_category), create_procurement(), get_all_procurements()
  - find_supplier: returns first supplier whose drug_categories contains the given string
  - record_id format: PR-001, PR-002, ...

---

## 3. Percept and Action Summary

### StockMonitorAgent
| Percept | Action |
|---|---|
| STOCK_READING | set_stock() in DrugDatabase |
| STOCK_READING (severity CRITICAL/HIGH/MEDIUM, not alerted) | Send STOCK_ALERT to SupplyAssessmentAgent |

### SupplyAssessmentAgent
| Percept | Action |
|---|---|
| STOCK_ALERT (new shortage) | Register in active_shortages; send SHORTAGE_CLASSIFIED |
| STOCK_ALERT (duplicate) | No action |

### TransferCoordinationAgent
| Percept | Action |
|---|---|
| SHORTAGE_CLASSIFIED (CONTROLLED) | Create FAILED TransferRecord; send TRANSFER_RESULT(success=False) |
| SHORTAGE_CLASSIFIED (not CONTROLLED, donor found) | Update stocks; create COMPLETED TransferRecord; send TRANSFER_RESULT(success=True) |
| SHORTAGE_CLASSIFIED (not CONTROLLED, no donor) | Create FAILED TransferRecord; send TRANSFER_RESULT(success=False) |

### ProcurementEscalationAgent
| Percept/Trigger | Action |
|---|---|
| SHORTAGE_CLASSIFIED (await=True) | Store in _awaiting_transfer |
| SHORTAGE_CLASSIFIED (await=False, MEDIUM) | Call _initiate_procurement() |
| TRANSFER_RESULT (success=True) | Mark shortage resolved |
| TRANSFER_RESULT (success=False) | Call _initiate_procurement() |
| proactive_step() each cycle | Check and escalate overdue procurements |
| simulate_supplier_confirmation() | Mark procurement CONFIRMED |

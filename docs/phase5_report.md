# Phase 5 - Implementation Report
## MedStock: Hospital Pharmacy Stock Depletion and Emergency Resupply Coordination

**Student ID:** 11126585
**Course:** DCIT 403 - Intelligent Agent Systems
**Methodology:** Prometheus (Padgham and Winikoff, 2004)

---

## Implementation Report

### Platform and Language Justification

MedStock is implemented entirely in Python 3 using the standard library only. Python was chosen for its readability, its support for dataclasses and enums which directly map to the belief structures defined in Phase 4, and its tkinter module which provides a cross-platform graphical user interface without any external dependencies. The decision to restrict the implementation to the standard library was deliberate: it ensures that the system can be run on any university laboratory computer without requiring a package manager, a virtual environment with third-party packages, or an internet connection. The standard library provides everything needed for agent communication (deque-based mailboxes), data modelling (dataclasses, enums), and the user interface (tkinter, ttk).

The Prometheus methodology does not prescribe a specific language or agent framework. Padgham and Winikoff (2004) describe Prometheus in terms of design artefacts, specifically system specification, architectural design, interaction design, and detailed design, all of which can be implemented in any sufficiently expressive language. Python satisfies these requirements and adds practical advantages for a course project: rapid iteration, clear syntax, and a self-contained deployment.

### Mapping from Prometheus Design to Implementation

The Phase 1 system specification defined the top-level goal, five sub-goal groups, nineteen functionalities, and three simulation scenarios. All nineteen functionalities are implemented. The three scenarios produce the exact outcomes described in Phase 1: Scenario 1 (Insulin ICU) resolves via transfer TR-001 at step 1; Scenario 2 (Morphine SURGICAL) escalates procurement PR-001 at step 8; Scenario 3a (Amoxicillin SURGICAL) resolves via transfer TR-003 at step 8; Scenario 3b (Paracetamol GENERAL) confirms procurement PR-002 at step 14.

The Phase 2 architectural design identified four agent types and their acquaintance relationships. These map directly to four Python classes in src/agents/: StockMonitorAgent, SupplyAssessmentAgent, TransferCoordinationAgent, and ProcurementEscalationAgent. Each inherits from the base Agent class in src/core/agent.py, which provides the inbox deque, the send/receive interface, the log_callback mechanism, and the run_cycle method that the MedStockSimulator calls in the correct order each step.

The Phase 3 interaction design specified seven message performatives and the content dictionaries for each. These are implemented in src/core/message.py as a Performative enum and a Message dataclass. The interaction diagrams in Phase 3 map directly to the execution trace produced when the simulation runs, which can be verified by reading the Activity Log in the UI.

The Phase 4 detailed design specified capabilities, plans with context conditions, belief structures, and percept/action tables. The context conditions for plan selection in SupplyAssessmentAgent correspond to the if/elif chains in _plan_classify_shortage(). The ControlledDenialPlan and TransferSearchPlan in TransferCoordinationAgent are implemented as the two branches of _plan_coordinate_transfer(). The ProactiveEscalation capability is implemented in proactive_step() which the base class calls after processing the inbox. The belief structures (DrugDatabase, WardDatabase, SupplierDatabase) are implemented as Python classes in src/beliefs/.

### How Each Phase Is Reflected in Code

Phase 1 produced the environment description including the five drugs, five wards, three suppliers, and the sensor schedule. These appear verbatim in MedStockSimulator._setup_drugs(), _setup_wards(), _setup_suppliers(), _setup_initial_stock(), and _schedule_sensor_events() in src/simulation/simulator.py.

Phase 2 produced the agent type list and acquaintance diagram. The AgentSystem class in src/core/agent_system.py implements the message routing layer. Agents register with the system by name and send messages by recipient name. The acquaintance relationships are enforced by hard-coded recipient strings in each agent's send() calls.

Phase 3 produced the interaction diagrams. These are verified at runtime by inspecting the simulation log, which shows each STOCK_READING, STOCK_ALERT, SHORTAGE_CLASSIFIED, and TRANSFER_RESULT in chronological order.

Phase 4 produced the detailed plan logic. The most complex plan is _plan_coordinate_transfer() in TransferCoordinationAgent, which iterates all wards, computes surplus ratios, selects a donor, calculates a safe transfer quantity, updates two stock records, creates a transfer record, and sends a result message. This corresponds exactly to the TransferSearchPlan described in Phase 4.

### Challenges and Limitations

The most significant design challenge was the handling of CRITICAL shortages where both the TransferCoordinationAgent and ProcurementEscalationAgent receive SHORTAGE_CLASSIFIED simultaneously. The procurement agent must not initiate procurement until it knows whether the transfer succeeded, but it also must not block waiting for the result. This was resolved using a simple _awaiting_transfer dictionary: the agent stores the classified content when it receives SHORTAGE_CLASSIFIED with await_transfer_result=True, and only calls _initiate_procurement() when the subsequent TRANSFER_RESULT arrives with success=False.

A second challenge was the escalation timing. The escalation timeout counts from dispatch_step, which is the value of current_step when _initiate_procurement() is called. Since all agents run in a fixed order within each simulation step (StockMonitor, SupplyAssessment, TransferCoord, Procurement), the dispatch_step for a morphine procurement initiated at step 3 is indeed 3. The escalation check at step 8 correctly computes 8-3=5 which equals the timeout.

The primary limitation of the implementation is that it operates in a closed simulation environment. The PharmacySensor fires pre-scheduled events rather than receiving live data from a real pharmacy system. The supplier confirmation at step 14 is injected directly by the simulator rather than arriving from an external API. Extending MedStock to connect to a real hospital information system would require replacing PharmacySensor with a network-connected sensor adapter and replacing the confirmation injection with a webhook listener. These extensions are architecturally straightforward given the separation of concerns enforced by the agent design.

A secondary limitation is that the simulation runs for a fixed 20 steps. Extending this to a continuous-running system would require converting the step-based loop into an event loop driven by real-time sensor data. The base Agent class already supports this extension since run_cycle() can be called at any interval.

### Conclusion

MedStock demonstrates that the Prometheus methodology produces a coherent, verifiable, and extensible multi-agent system design. The four-phase design process from system specification through detailed design produced a direct mapping to the Python implementation with no design decisions left unaccounted for. The resulting system correctly handles all three simulation scenarios, enforces the controlled substance regulatory policy, performs proactive escalation monitoring every cycle, and provides a professional graphical interface for visualising and interacting with the simulation in real time.

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.theme import COLORS, FONTS
from src.simulation.simulator import MedStockSimulator
from src.core.message import Message, Performative
from src.beliefs.drug_belief import SeverityLevel


def make_button(parent, text, command, color_key="button_primary", **kwargs):
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=COLORS[color_key],
        fg="#ffffff",
        activebackground=COLORS[color_key],
        activeforeground="#ffffff",
        relief="flat",
        font=FONTS["small"],
        padx=10,
        pady=4,
        cursor="hand2",
        **kwargs
    )
    return btn


def make_panel(parent, title, **kwargs):
    frame = tk.Frame(parent, bg=COLORS["bg_panel"], relief="flat",
                     highlightbackground=COLORS["border"], highlightthickness=1, **kwargs)
    header = tk.Frame(frame, bg=COLORS["bg_panel_header"], pady=4)
    header.pack(fill="x")
    tk.Label(
        header,
        text=title,
        font=FONTS["panel_header"],
        bg=COLORS["bg_panel_header"],
        fg=COLORS["accent"],
        padx=8
    ).pack(side="left")
    content = tk.Frame(frame, bg=COLORS["bg_panel"])
    content.pack(fill="both", expand=True, padx=2, pady=2)
    return frame, content, header


class MedStockApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MedStock - Hospital Pharmacy Intelligence System")
        self.geometry("1400x860")
        self.minsize(1100, 700)
        self.configure(bg=COLORS["bg_main"])
        self._auto_running = False
        self._after_id = None
        self._stock_sort_reverse = {}
        self.simulator = MedStockSimulator(log_callback=self._on_log)
        self._build_ui()
        self.refresh_display()

    def _on_log(self, text):
        self._append_log(text)

    def _build_ui(self):
        self._build_header()
        self._build_manual_input()
        self._build_main_body()
        self._build_status_bar()

    def _build_header(self):
        self.header_frame = tk.Frame(self, bg=COLORS["bg_header"], pady=8)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.grid_columnconfigure(0, weight=1)

        left = tk.Frame(self.header_frame, bg=COLORS["bg_header"])
        left.pack(side="left", padx=16)

        tk.Label(
            left, text="MedStock",
            font=FONTS["large_bold"],
            bg=COLORS["bg_header"],
            fg=COLORS["fg_header"]
        ).pack(anchor="w")
        tk.Label(
            left, text="Hospital Pharmacy Intelligence System",
            font=FONTS["small"],
            bg=COLORS["bg_header"],
            fg="#90caf9"
        ).pack(anchor="w")

        right = tk.Frame(self.header_frame, bg=COLORS["bg_header"])
        right.pack(side="right", padx=16)

        self.step_label = tk.Label(
            right,
            text="Step: 0 / 20",
            font=FONTS["header"],
            bg=COLORS["bg_header"],
            fg=COLORS["fg_header"]
        )
        self.step_label.pack(side="left", padx=(0, 12))

        self.step_btn = make_button(right, "Step", self._do_step, "button_primary")
        self.step_btn.pack(side="left", padx=3)

        self.auto_btn = make_button(right, "Auto Run", self._toggle_auto, "button_success")
        self.auto_btn.pack(side="left", padx=3)

        tk.Label(
            right, text="Speed (s/step):",
            font=FONTS["small"],
            bg=COLORS["bg_header"],
            fg=COLORS["fg_header"]
        ).pack(side="left", padx=(10, 2))

        self.speed_scale = tk.Scale(
            right,
            from_=0.5,
            to=3.0,
            resolution=0.5,
            orient="horizontal",
            length=100,
            bg=COLORS["bg_header"],
            fg=COLORS["fg_header"],
            troughcolor="#1a4a8a",
            highlightthickness=0,
            font=FONTS["small"]
        )
        self.speed_scale.set(1.0)
        self.speed_scale.pack(side="left", padx=4)

        self.reset_btn = make_button(right, "Reset", self._do_reset, "button_danger")
        self.reset_btn.pack(side="left", padx=(8, 0))

    def _build_manual_input(self):
        frame = tk.Frame(self, bg="#e8edf5", pady=5, padx=10)
        frame.grid(row=1, column=0, sticky="ew")

        tk.Label(
            frame, text="Manual Stock Input:",
            font=FONTS["header"],
            bg="#e8edf5",
            fg=COLORS["fg_main"]
        ).pack(side="left", padx=(0, 8))

        tk.Label(frame, text="Drug:", font=FONTS["small"], bg="#e8edf5").pack(side="left")
        self.manual_drug_var = tk.StringVar()
        drug_names = [d.name for d in self.simulator.drug_db.get_all_drugs()]
        self.drug_combo = ttk.Combobox(
            frame, textvariable=self.manual_drug_var,
            values=drug_names, width=14, state="readonly", font=FONTS["small"]
        )
        if drug_names:
            self.drug_combo.current(0)
        self.drug_combo.pack(side="left", padx=(2, 8))

        tk.Label(frame, text="Ward:", font=FONTS["small"], bg="#e8edf5").pack(side="left")
        self.manual_ward_var = tk.StringVar()
        ward_ids = [w.ward_id for w in self.simulator.ward_db.get_all_wards()]
        self.ward_combo = ttk.Combobox(
            frame, textvariable=self.manual_ward_var,
            values=ward_ids, width=12, state="readonly", font=FONTS["small"]
        )
        if ward_ids:
            self.ward_combo.current(0)
        self.ward_combo.pack(side="left", padx=(2, 8))

        tk.Label(frame, text="Quantity:", font=FONTS["small"], bg="#e8edf5").pack(side="left")
        self.manual_qty_var = tk.StringVar(value="50")
        qty_entry = tk.Entry(
            frame, textvariable=self.manual_qty_var, width=7,
            font=FONTS["small"], relief="solid", bd=1
        )
        qty_entry.pack(side="left", padx=(2, 8))

        make_button(
            frame, "Submit Reading", self._submit_manual_reading, "button_neutral"
        ).pack(side="left")

    def _build_main_body(self):
        self.body_frame = tk.Frame(self, bg=COLORS["bg_main"])
        self.body_frame.grid(row=2, column=0, sticky="nsew", padx=6, pady=6)
        self.grid_rowconfigure(2, weight=1)

        self.body_frame.grid_columnconfigure(0, weight=40)
        self.body_frame.grid_columnconfigure(1, weight=60)
        self.body_frame.grid_rowconfigure(0, weight=45)
        self.body_frame.grid_rowconfigure(1, weight=55)

        self._build_stock_panel()
        self._build_alerts_panel()
        self._build_operations_panel()
        self._build_log_panel()

    def _build_stock_panel(self):
        panel, content, _ = make_panel(self.body_frame, "DRUG STOCK LEVELS")
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 3), pady=(0, 3))

        cols = ("Drug", "Category", "Ward", "Stock", "Threshold", "Level%", "Status")
        self.stock_tree = ttk.Treeview(
            content, columns=cols, show="headings", selectmode="browse"
        )

        col_widths = {
            "Drug": 90, "Category": 80, "Ward": 80, "Stock": 60,
            "Threshold": 75, "Level%": 60, "Status": 75
        }
        for col in cols:
            self.stock_tree.heading(col, text=col,
                                    command=lambda c=col: self._sort_stock(c))
            self.stock_tree.column(col, width=col_widths.get(col, 70),
                                   minwidth=50, anchor="center")

        self.stock_tree.tag_configure(
            "critical_row", background=COLORS["critical_bg"], foreground=COLORS["critical"])
        self.stock_tree.tag_configure(
            "high_row", background=COLORS["high_bg"], foreground=COLORS["high"])
        self.stock_tree.tag_configure(
            "medium_row", background=COLORS["medium_bg"], foreground="#5d4037")
        self.stock_tree.tag_configure(
            "low_row", background=COLORS["low_bg"], foreground=COLORS["low"])
        self.stock_tree.tag_configure(
            "ok_row", background=COLORS["ok_bg"], foreground=COLORS["ok"])

        vsb = ttk.Scrollbar(content, orient="vertical", command=self.stock_tree.yview)
        hsb = ttk.Scrollbar(content, orient="horizontal", command=self.stock_tree.xview)
        self.stock_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.stock_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(0, weight=1)

    def _sort_stock(self, col):
        items = [(self.stock_tree.set(k, col), k) for k in self.stock_tree.get_children("")]
        rev = self._stock_sort_reverse.get(col, False)
        try:
            items.sort(reverse=rev, key=lambda x: float(x[0].replace("%", "")))
        except ValueError:
            items.sort(reverse=rev, key=lambda x: x[0].lower())
        for index, (_, k) in enumerate(items):
            self.stock_tree.move(k, "", index)
        self._stock_sort_reverse[col] = not rev

    def _build_alerts_panel(self):
        panel, content, _ = make_panel(self.body_frame, "ACTIVE ALERTS")
        panel.grid(row=0, column=1, sticky="nsew", padx=(3, 0), pady=(0, 3))

        cols = ("ID", "Drug", "Ward", "Severity", "Category", "Step Detected", "Status")
        self.alerts_tree = ttk.Treeview(
            content, columns=cols, show="headings", selectmode="browse"
        )
        col_widths = {
            "ID": 120, "Drug": 90, "Ward": 80, "Severity": 75,
            "Category": 80, "Step Detected": 95, "Status": 80
        }
        for col in cols:
            self.alerts_tree.heading(col, text=col)
            self.alerts_tree.column(col, width=col_widths.get(col, 80),
                                    minwidth=50, anchor="center")

        self.alerts_tree.tag_configure(
            "critical_row", background=COLORS["critical_bg"], foreground=COLORS["critical"])
        self.alerts_tree.tag_configure(
            "high_row", background=COLORS["high_bg"], foreground=COLORS["high"])
        self.alerts_tree.tag_configure(
            "medium_row", background=COLORS["medium_bg"], foreground="#5d4037")
        self.alerts_tree.tag_configure(
            "resolved_row", background=COLORS["resolved_bg"], foreground=COLORS["resolved"])
        self.alerts_tree.tag_configure(
            "escalated_row", background=COLORS["escalated_bg"], foreground=COLORS["escalated"])

        vsb = ttk.Scrollbar(content, orient="vertical", command=self.alerts_tree.yview)
        hsb = ttk.Scrollbar(content, orient="horizontal", command=self.alerts_tree.xview)
        self.alerts_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.alerts_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(0, weight=1)

    def _build_operations_panel(self):
        panel, content, _ = make_panel(self.body_frame, "OPERATIONS")
        panel.grid(row=1, column=0, sticky="nsew", padx=(0, 3), pady=(3, 0))

        self.ops_notebook = ttk.Notebook(content)
        self.ops_notebook.pack(fill="both", expand=True)

        self._build_transfers_tab()
        self._build_procurement_tab()
        self._build_expiry_tab()

    def _build_transfers_tab(self):
        tab = tk.Frame(self.ops_notebook, bg=COLORS["bg_panel"])
        self.ops_notebook.add(tab, text="  Transfers  ")

        cols = ("Transfer ID", "Drug", "From Ward", "To Ward", "Qty", "Status", "Step")
        self.transfer_tree = ttk.Treeview(
            tab, columns=cols, show="headings", selectmode="browse"
        )
        col_widths = {
            "Transfer ID": 80, "Drug": 90, "From Ward": 80,
            "To Ward": 80, "Qty": 60, "Status": 80, "Step": 50
        }
        for col in cols:
            self.transfer_tree.heading(col, text=col)
            self.transfer_tree.column(col, width=col_widths.get(col, 70),
                                      minwidth=40, anchor="center")

        self.transfer_tree.tag_configure(
            "completed_row", background=COLORS["confirmed_bg"], foreground=COLORS["confirmed"])
        self.transfer_tree.tag_configure(
            "failed_row", background=COLORS["critical_bg"], foreground=COLORS["critical"])
        self.transfer_tree.tag_configure(
            "pending_row", background=COLORS["requested_bg"], foreground=COLORS["requested"])

        vsb = ttk.Scrollbar(tab, orient="vertical", command=self.transfer_tree.yview)
        self.transfer_tree.configure(yscrollcommand=vsb.set)

        self.transfer_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

    def _build_procurement_tab(self):
        tab = tk.Frame(self.ops_notebook, bg=COLORS["bg_panel"])
        self.ops_notebook.add(tab, text="  Procurement  ")

        cols = ("Record ID", "Drug", "Supplier", "Qty", "Status", "Step", "Escalated")
        self.proc_tree = ttk.Treeview(
            tab, columns=cols, show="headings", selectmode="browse"
        )
        col_widths = {
            "Record ID": 75, "Drug": 90, "Supplier": 140,
            "Qty": 55, "Status": 85, "Step": 50, "Escalated": 75
        }
        for col in cols:
            self.proc_tree.heading(col, text=col)
            self.proc_tree.column(col, width=col_widths.get(col, 80),
                                  minwidth=40, anchor="center")

        self.proc_tree.tag_configure(
            "confirmed_row", background=COLORS["confirmed_bg"], foreground=COLORS["confirmed"])
        self.proc_tree.tag_configure(
            "escalated_row", background=COLORS["escalated_bg"], foreground=COLORS["escalated"])
        self.proc_tree.tag_configure(
            "requested_row", background=COLORS["requested_bg"], foreground=COLORS["requested"])

        vsb = ttk.Scrollbar(tab, orient="vertical", command=self.proc_tree.yview)
        self.proc_tree.configure(yscrollcommand=vsb.set)

        self.proc_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

    def _build_expiry_tab(self):
        tab = tk.Frame(self.ops_notebook, bg=COLORS["bg_panel"])
        self.ops_notebook.add(tab, text="  Expiry Monitor  ")

        cols = ("Batch ID", "Drug", "Ward", "Qty", "Exp Step", "Status", "Detected")
        self.expiry_tree = ttk.Treeview(
            tab, columns=cols, show="headings", selectmode="browse"
        )
        col_widths = {
            "Batch ID": 75, "Drug": 90, "Ward": 80,
            "Qty": 55, "Exp Step": 70, "Status": 110, "Detected": 65
        }
        for col in cols:
            self.expiry_tree.heading(col, text=col)
            self.expiry_tree.column(col, width=col_widths.get(col, 75),
                                    minwidth=40, anchor="center")

        self.expiry_tree.tag_configure(
            "expired_row",
            background=COLORS["expiry_expired_bg"],
            foreground=COLORS["expiry_expired"])
        self.expiry_tree.tag_configure(
            "expiring_soon_row",
            background=COLORS["expiry_soon_bg"],
            foreground=COLORS["expiry_soon"])
        self.expiry_tree.tag_configure(
            "warning_row",
            background=COLORS["expiry_warning_bg"],
            foreground=COLORS["expiry_warning"])
        self.expiry_tree.tag_configure(
            "ok_row", background=COLORS["ok_bg"], foreground=COLORS["ok"])

        vsb = ttk.Scrollbar(tab, orient="vertical", command=self.expiry_tree.yview)
        self.expiry_tree.configure(yscrollcommand=vsb.set)

        self.expiry_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

    def _build_log_panel(self):
        panel, content, header = make_panel(self.body_frame, "ACTIVITY LOG")
        panel.grid(row=1, column=1, sticky="nsew", padx=(3, 0), pady=(3, 0))

        make_button(
            header, "Clear Log", self._clear_log, "button_neutral"
        ).pack(side="right", padx=8)

        self.log_text = tk.Text(
            content,
            font=FONTS["mono"],
            bg="#1e2736",
            fg="#e0e0e0",
            insertbackground="#ffffff",
            relief="flat",
            wrap="word",
            state="disabled",
            padx=6,
            pady=4
        )

        vsb = ttk.Scrollbar(content, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=vsb.set)

        self.log_text.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.log_text.tag_configure("stock", foreground="#64b5f6")
        self.log_text.tag_configure("assessment", foreground="#ce93d8")
        self.log_text.tag_configure("transfer", foreground="#ffb74d")
        self.log_text.tag_configure("procurement", foreground="#ef9a9a")
        self.log_text.tag_configure("expiry", foreground="#4db6ac")
        self.log_text.tag_configure("system", foreground="#80cbc4")
        self.log_text.tag_configure(
            "system_bold", foreground="#80cbc4", font=("Consolas", 9, "bold"))

    def _build_status_bar(self):
        self.status_bar = tk.Frame(self, bg="#37474f", pady=4)
        self.status_bar.grid(row=3, column=0, sticky="ew")

        self.status_label = tk.Label(
            self.status_bar,
            text="Step: 0/20 | Alerts: 0 | Transfers: 0 | Procurements: 0 | Status: IDLE",
            font=FONTS["small"],
            bg="#37474f",
            fg="#e0e0e0",
            padx=12
        )
        self.status_label.pack(side="left")

    def _append_log(self, text):
        self.log_text.configure(state="normal")
        if text.startswith("--- STEP"):
            self.log_text.insert("end", "\n" + text + "\n", "system_bold")
        elif "[StockMonitorAgent]" in text:
            self.log_text.insert("end", text + "\n", "stock")
        elif "[SupplyAssessmentAgent]" in text:
            self.log_text.insert("end", text + "\n", "assessment")
        elif "[TransferCoordinationAgent]" in text:
            self.log_text.insert("end", text + "\n", "transfer")
        elif "[ProcurementEscalationAgent]" in text:
            self.log_text.insert("end", text + "\n", "procurement")
        elif "[ExpiryMonitorAgent]" in text:
            self.log_text.insert("end", text + "\n", "expiry")
        else:
            self.log_text.insert("end", text + "\n", "system")
        self.log_text.configure(state="disabled")
        self.log_text.see("end")

    def _clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    def refresh_display(self):
        self._refresh_stock_panel()
        self._refresh_alerts_panel()
        self._refresh_transfers_panel()
        self._refresh_procurement_panel()
        self._refresh_expiry_panel()
        self._refresh_status_bar()
        self._refresh_header_step()
        self._update_button_states()

    def _refresh_stock_panel(self):
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)

        stocks = self.simulator.get_stock_summary()
        severity_order = {
            SeverityLevel.CRITICAL: 0,
            SeverityLevel.HIGH: 1,
            SeverityLevel.MEDIUM: 2,
            SeverityLevel.LOW: 3,
            SeverityLevel.OK: 4
        }
        stocks_sorted = sorted(stocks, key=lambda r: severity_order.get(r.severity(), 5))

        for record in stocks_sorted:
            drug = self.simulator.drug_db.get_drug(record.drug_id)
            if not drug:
                continue
            sev = record.severity()
            level_pct = (record.current_stock / record.reorder_threshold * 100
                         if record.reorder_threshold > 0 else 0)
            tag = self._severity_tag(sev)
            self.stock_tree.insert("", "end", values=(
                drug.name,
                drug.category.value,
                record.ward_id,
                int(record.current_stock),
                int(record.reorder_threshold),
                f"{level_pct:.1f}%",
                sev.value
            ), tags=(tag,))

    def _severity_tag(self, severity):
        mapping = {
            SeverityLevel.CRITICAL: "critical_row",
            SeverityLevel.HIGH: "high_row",
            SeverityLevel.MEDIUM: "medium_row",
            SeverityLevel.LOW: "low_row",
            SeverityLevel.OK: "ok_row"
        }
        return mapping.get(severity, "ok_row")

    def _refresh_alerts_panel(self):
        for item in self.alerts_tree.get_children():
            self.alerts_tree.delete(item)

        proc_agent = self.simulator.procurement_escalation
        resolved = proc_agent.resolved_shortages
        assessment_agent = self.simulator.supply_assessment
        active = assessment_agent.active_shortages
        pending_proc = proc_agent.pending_procurements

        all_shortage_ids = set(list(active.keys()) + list(resolved.keys()))

        for sid in all_shortage_ids:
            if sid in active:
                info = active[sid]
            else:
                r = resolved[sid]
                info = {
                    "shortage_id": sid,
                    "drug_name": r.get("drug_name", sid),
                    "ward_id": r.get("ward_id", ""),
                    "severity": "MEDIUM",
                    "category": "",
                    "step_detected": r.get("step", 0)
                }

            sev = info.get("severity", "")
            step_det = info.get("step_detected", "")
            cat = info.get("category", "")
            drug_name = info.get("drug_name", "")
            ward = info.get("ward_id", "")

            if sid in resolved and sid not in pending_proc:
                status = "RESOLVED"
                tag = "resolved_row"
            elif sid in pending_proc:
                proc_status = pending_proc[sid]["status"].value
                if proc_status == "ESCALATED":
                    status = "ESCALATED"
                    tag = "escalated_row"
                elif proc_status == "CONFIRMED":
                    status = "CONFIRMED"
                    tag = "resolved_row"
                else:
                    status = "PROCUREMENT"
                    tag = self._sev_alert_tag(sev)
            else:
                status = "ACTIVE"
                tag = self._sev_alert_tag(sev)

            self.alerts_tree.insert("", "end", values=(
                sid, drug_name, ward, sev, cat, step_det, status
            ), tags=(tag,))

    def _sev_alert_tag(self, sev_str):
        mapping = {
            "CRITICAL": "critical_row",
            "HIGH": "high_row",
            "MEDIUM": "medium_row"
        }
        return mapping.get(sev_str, "ok_row")

    def _refresh_transfers_panel(self):
        for item in self.transfer_tree.get_children():
            self.transfer_tree.delete(item)

        for tr in self.simulator.get_transfers():
            status = tr.status.value
            if status == "COMPLETED":
                tag = "completed_row"
            elif status == "FAILED":
                tag = "failed_row"
            else:
                tag = "pending_row"
            self.transfer_tree.insert("", "end", values=(
                tr.transfer_id,
                tr.drug_name,
                tr.from_ward_id,
                tr.to_ward_id,
                int(tr.quantity),
                status,
                tr.initiated_step
            ), tags=(tag,))

    def _refresh_procurement_panel(self):
        for item in self.proc_tree.get_children():
            self.proc_tree.delete(item)

        for pr in self.simulator.get_procurements():
            status = pr.status.value
            if status == "CONFIRMED":
                tag = "confirmed_row"
            elif status == "ESCALATED":
                tag = "escalated_row"
            else:
                tag = "requested_row"
            escalated_step = pr.escalated_step if pr.escalated_step >= 0 else "-"
            self.proc_tree.insert("", "end", values=(
                pr.record_id,
                pr.drug_name,
                pr.supplier_name,
                int(pr.quantity_requested),
                status,
                pr.requested_step,
                escalated_step
            ), tags=(tag,))

    def _refresh_expiry_panel(self):
        for item in self.expiry_tree.get_children():
            self.expiry_tree.delete(item)

        alerts = self.simulator.expiry_monitor.expiry_alerts
        status_order = {"EXPIRED": 0, "EXPIRING_SOON": 1, "WARNING": 2, "OK": 3}
        sorted_alerts = sorted(
            alerts.values(),
            key=lambda a: (status_order.get(a["status"], 9), a["expiry_step"])
        )

        for alert in sorted_alerts:
            status = alert["status"]
            if status == "EXPIRED":
                tag = "expired_row"
            elif status == "EXPIRING_SOON":
                tag = "expiring_soon_row"
            elif status == "WARNING":
                tag = "warning_row"
            else:
                tag = "ok_row"
            self.expiry_tree.insert("", "end", values=(
                alert["batch_id"],
                alert["drug_name"],
                alert["ward_id"],
                int(alert["quantity"]),
                alert["expiry_step"],
                status,
                alert["detected_step"],
            ), tags=(tag,))

    def _refresh_status_bar(self):
        step = self.simulator.current_step
        total = self.simulator.total_steps
        alerts = len(self.simulator.supply_assessment.active_shortages)
        transfers = len(self.simulator.get_transfers())
        procs = len(self.simulator.get_procurements())
        expiry_alerts = len(self.simulator.expiry_monitor.expiry_alerts)

        if self.simulator.finished:
            status_str = "COMPLETE"
        elif self._auto_running:
            status_str = "RUNNING"
        else:
            status_str = "IDLE"

        self.status_label.configure(
            text=(f"Step: {step}/{total} | Alerts: {alerts} | "
                  f"Transfers: {transfers} | Procurements: {procs} | "
                  f"Expiry Alerts: {expiry_alerts} | Status: {status_str}")
        )

    def _refresh_header_step(self):
        step = self.simulator.current_step
        total = self.simulator.total_steps
        self.step_label.configure(text=f"Step: {step} / {total}")

    def _update_button_states(self):
        finished = self.simulator.finished
        state = "disabled" if finished else "normal"
        self.step_btn.configure(state=state)
        self.auto_btn.configure(state=state)

    def _do_step(self):
        if self.simulator.finished:
            return
        self.simulator.step()
        self.refresh_display()

    def _toggle_auto(self):
        if self._auto_running:
            self._auto_running = False
            if self._after_id:
                self.after_cancel(self._after_id)
                self._after_id = None
            self.auto_btn.configure(text="Auto Run", bg=COLORS["button_success"])
            self._refresh_status_bar()
        else:
            if self.simulator.finished:
                return
            self._auto_running = True
            self.auto_btn.configure(text="Pause", bg=COLORS["button_danger"])
            self._refresh_status_bar()
            self._auto_step()

    def _auto_step(self):
        if not self._auto_running:
            return
        if self.simulator.finished:
            self._auto_running = False
            self.auto_btn.configure(text="Auto Run", bg=COLORS["button_success"])
            self.refresh_display()
            return
        self.simulator.step()
        self.refresh_display()
        delay_ms = int(self.speed_scale.get() * 1000)
        self._after_id = self.after(delay_ms, self._auto_step)

    def _do_reset(self):
        if self._auto_running:
            self._toggle_auto()
        self._clear_log()
        self.simulator = MedStockSimulator(log_callback=self._on_log)
        self._rebuild_combos()
        self.refresh_display()

    def _rebuild_combos(self):
        drug_names = [d.name for d in self.simulator.drug_db.get_all_drugs()]
        ward_ids = [w.ward_id for w in self.simulator.ward_db.get_all_wards()]
        self.drug_combo.configure(values=drug_names)
        self.ward_combo.configure(values=ward_ids)
        if drug_names:
            self.drug_combo.current(0)
        if ward_ids:
            self.ward_combo.current(0)

    def _submit_manual_reading(self):
        drug_name = self.manual_drug_var.get()
        ward_id = self.manual_ward_var.get()
        qty_str = self.manual_qty_var.get().strip()

        if not drug_name or not ward_id:
            messagebox.showwarning("Input Error", "Please select a drug and ward.")
            return

        try:
            qty = int(qty_str)
        except ValueError:
            messagebox.showwarning("Input Error", "Quantity must be an integer.")
            return

        drug_id = None
        for d in self.simulator.drug_db.get_all_drugs():
            if d.name == drug_name:
                drug_id = d.drug_id
                break

        if drug_id is None:
            messagebox.showwarning("Input Error", "Drug not found.")
            return

        step = self.simulator.current_step

        msg = Message(
            performative=Performative.STOCK_READING,
            sender="ManualInput",
            recipient="StockMonitorAgent",
            content={
                "drug_id": drug_id,
                "ward_id": ward_id,
                "quantity": qty,
                "step": step
            }
        )
        self.simulator.agent_system.deliver(msg)
        self.simulator.stock_monitor.run_cycle(step)
        self.simulator.supply_assessment.run_cycle(step)
        self.simulator.transfer_coord.run_cycle(step)
        self.simulator.expiry_monitor.run_cycle(step)
        self.simulator.procurement_escalation.run_cycle(step)
        self.refresh_display()

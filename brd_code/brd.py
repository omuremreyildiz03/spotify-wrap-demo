import subprocess, sys, os

# ── Hide console window on Windows (double-click launch) ─────────────────────
if sys.platform == "win32":
    try:
        import ctypes
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)  # SW_HIDE
    except Exception:
        pass

REQUIRED = ["pandas", "openpyxl"]
def ensure_packages():
    for pkg in REQUIRED:
        try:
            __import__(pkg)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", pkg],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
ensure_packages()

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

# ── Config ────────────────────────────────────────────────────────────────────
EXCEL_FILE    = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db.xlsx")
COL_DRB       = "DRB"
COL_CONS_NAME = "Consumable_Name"
COL_CONS_CODE = "Consumable_Code"
COL_SOL_NAME  = "Solution_Name"
COL_SOL_CODE  = "Solution_Code"
COL_MATERIAL  = "Material"
COL_TEST      = "Test"

# ── Data ──────────────────────────────────────────────────────────────────────
def load_data():
    if not os.path.exists(EXCEL_FILE):
        messagebox.showerror("Error", f"Database file not found:\n{EXCEL_FILE}")
        sys.exit(1)
    df = pd.read_excel(EXCEL_FILE, dtype=str).fillna("")
    df = df.apply(lambda col: col.map(lambda x: x.strip() if isinstance(x, str) else x))
    db = {}
    for _, row in df.iterrows():
        drb = row.get(COL_DRB, "").strip()
        if not drb:
            continue
        def split_cell(val):
            return [v.strip() for v in str(val).split(",") if v.strip()]
        entry = db.setdefault(drb, {
            "consumable_names": [], "consumable_codes": [],
            "solution_names":   [], "solution_codes":   [],
            "materials":        [], "tests":            [],
        })
        for v in split_cell(row.get(COL_CONS_NAME, "")):
            if v not in entry["consumable_names"]: entry["consumable_names"].append(v)
        for v in split_cell(row.get(COL_CONS_CODE, "")):
            if v not in entry["consumable_codes"]: entry["consumable_codes"].append(v)
        for v in split_cell(row.get(COL_SOL_NAME, "")):
            if v not in entry["solution_names"]: entry["solution_names"].append(v)
        for v in split_cell(row.get(COL_SOL_CODE, "")):
            if v not in entry["solution_codes"]: entry["solution_codes"].append(v)
        for v in split_cell(row.get(COL_MATERIAL, "")):
            if v not in entry["materials"]: entry["materials"].append(v)
        for v in split_cell(row.get(COL_TEST, "")):
            if v not in entry["tests"]: entry["tests"].append(v)
    return db

def get_all_options(db, type_key):
    names, codes, materials, tests = set(), set(), set(), set()
    for entry in db.values():
        if type_key == "Consumable":
            for v in entry["consumable_names"]: names.add(v)
            for v in entry["consumable_codes"]: codes.add(v)
        else:
            for v in entry["solution_names"]: names.add(v)
            for v in entry["solution_codes"]: codes.add(v)
        for v in entry["materials"]: materials.add(v)
        for v in entry["tests"]:     tests.add(v)
    return sorted(names), sorted(codes), sorted(materials), sorted(tests)

def filter_drbs(db, type_key, name_val, code_val, material_val, test_val):
    def active(v): return bool(v and v.strip())
    na, ca, ma, ta = active(name_val), active(code_val), active(material_val), active(test_val)
    if not any([na, ca, ma, ta]):
        return None
    results = []
    for drb, entry in db.items():
        nl = entry["consumable_names"] if type_key == "Consumable" else entry["solution_names"]
        cl = entry["consumable_codes"] if type_key == "Consumable" else entry["solution_codes"]
        if na or ca:
            nm = na and any(v.lower().startswith(name_val.lower()) for v in nl)
            cm = ca and any(v.lower().startswith(code_val.lower()) for v in cl)
            if not (nm or cm): continue
        if ma and not any(v.lower().startswith(material_val.lower()) for v in entry["materials"]): continue
        if ta and not any(v.lower().startswith(test_val.lower()) for v in entry["tests"]): continue
        results.append(drb)
    return results


# ── DropdownField ─────────────────────────────────────────────────────────────

class DropdownField(tk.Frame):
    """
    Plain Entry + Toplevel popup listbox. No placeholder.

    - Click  → open with full list (or filtered if text exists)
    - Type   → filter list live, fire on_change every key
    - Pick   → fill entry, close popup
    - Escape / click elsewhere → close popup, keep text
    """

    DROP_ROW_H  = 26
    DROP_MAX_H  = 200
    BORDER_IDLE = "#C8CCDC"
    BORDER_FOCUS= "#1B6B3A"
    ENTRY_BG    = "#FFFFFF"
    ENTRY_FG    = "#1A1D2E"
    DROP_BG     = "#FFFFFF"
    DROP_FG     = "#1A1D2E"
    DROP_SEL_BG = "#E6F2EC"
    DROP_SEL_FG = "#1B6B3A"
    FONT        = ("Segoe UI", 10)

    def __init__(self, master, all_values=None, on_change=None, **kwargs):
        kwargs.pop("bg", None)
        super().__init__(master, bg=self.ENTRY_BG, **kwargs)

        self._all             = list(all_values or [])
        self._on_change       = on_change
        self._popup           = None
        self._listbox         = None
        self._block_next_open = False

        self._border = tk.Frame(self, bg=self.BORDER_IDLE, padx=1, pady=1)
        self._border.pack(fill="both", expand=True)

        self._entry = tk.Entry(
            self._border,
            font=self.FONT,
            bg=self.ENTRY_BG,
            fg=self.ENTRY_FG,
            relief="flat", bd=4,
            insertbackground=self.BORDER_FOCUS,
            highlightthickness=0,
        )
        self._entry.pack(fill="both", expand=True)

        self._entry.bind("<FocusIn>",    self._on_focus_in)
        self._entry.bind("<FocusOut>",   self._on_focus_out)
        self._entry.bind("<Button-1>",   self._on_click)
        self._entry.bind("<KeyRelease>", self._on_key_release)
        self._entry.bind("<Escape>",     self._on_escape)
        self._entry.bind("<Return>",     self._on_return)
        self._entry.bind("<Up>",         self._on_arrow_up)
        self._entry.bind("<Down>",       self._on_arrow_down)

    # ── public ────────────────────────────────────────────────────────────────

    def set_all_values(self, values):
        self._all = list(values)

    def get_value(self):
        return self._entry.get().strip()

    def clear(self):
        self._close_popup()
        self._entry.delete(0, "end")
        self._block_next_open = False

    # ── helpers ───────────────────────────────────────────────────────────────

    def _filtered_list(self):
        typed = self._entry.get().strip()
        if not typed:
            return self._all
        return [v for v in self._all if v.lower().startswith(typed.lower())]

    # ── focus / click ─────────────────────────────────────────────────────────

    def _on_focus_in(self, event=None):
        self._border.config(bg=self.BORDER_FOCUS)
        if self._block_next_open:
            self._block_next_open = False
            return
        self._show_popup(self._filtered_list())

    def _on_click(self, event=None):
        if self._popup is not None:
            self._close_popup()
            return
        self._show_popup(self._filtered_list())

    def _on_focus_out(self, event=None):
        self._border.config(bg=self.BORDER_IDLE)
        self.after(150, self._handle_focus_out)

    def _handle_focus_out(self):
        try:
            focused = self.focus_get()
        except Exception:
            focused = None
        if self._listbox is not None and focused is self._listbox:
            return
        self._close_popup()

    # ── keyboard ──────────────────────────────────────────────────────────────

    def _on_escape(self, event=None):
        self._close_popup()
        try:
            self.master.focus_set()
        except Exception:
            pass

    def _on_key_release(self, event=None):
        if event and event.keysym in (
            "Escape", "Return", "Up", "Down",
            "Left", "Right", "Shift_L", "Shift_R",
            "Control_L", "Control_R", "Tab",
        ):
            return
        self._show_popup(self._filtered_list())
        if self._on_change:
            self._on_change()

    def _on_return(self, event=None):
        if self._listbox:
            sel = self._listbox.curselection()
            if sel:
                self._pick(self._listbox.get(sel[0]))
                return
        self._close_popup()
        if self._on_change:
            self._on_change()

    def _on_arrow_down(self, event=None):
        if self._listbox is None:
            self._show_popup(self._filtered_list())
            return
        cur  = self._listbox.curselection()
        nxt  = (cur[0] + 1) if cur else 0
        if nxt < self._listbox.size():
            self._listbox.selection_clear(0, "end")
            self._listbox.selection_set(nxt)
            self._listbox.activate(nxt)
            self._listbox.see(nxt)

    def _on_arrow_up(self, event=None):
        if self._listbox is None:
            return
        cur = self._listbox.curselection()
        if not cur:
            return
        prev = cur[0] - 1
        if prev >= 0:
            self._listbox.selection_clear(0, "end")
            self._listbox.selection_set(prev)
            self._listbox.activate(prev)
            self._listbox.see(prev)

    # ── popup ─────────────────────────────────────────────────────────────────

    def _show_popup(self, items):
        if not items:
            self._close_popup()
            return

        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        w = self.winfo_width()
        h = min(len(items) * self.DROP_ROW_H + 4, self.DROP_MAX_H)

        if self._popup is None:
            self._popup = tk.Toplevel(self)
            self._popup.wm_overrideredirect(True)
            self._popup.wm_attributes("-topmost", True)

            outer = tk.Frame(self._popup, bg=self.BORDER_IDLE, padx=1, pady=1)
            outer.pack(fill="both", expand=True)

            self._listbox = tk.Listbox(
                outer,
                font=self.FONT,
                bg=self.DROP_BG, fg=self.DROP_FG,
                selectbackground=self.DROP_SEL_BG,
                selectforeground=self.DROP_SEL_FG,
                relief="flat", bd=0,
                activestyle="none",
                highlightthickness=0,
            )
            self._listbox.pack(side="left", fill="both", expand=True)

            sb = tk.Scrollbar(outer, orient="vertical",
                              command=self._listbox.yview, width=12)
            sb.pack(side="right", fill="y")
            self._listbox.config(yscrollcommand=sb.set)

            self._listbox.bind("<ButtonRelease-1>", self._on_list_click)
            self._listbox.bind("<FocusOut>",        self._on_list_focus_out)

        self._popup.geometry(f"{w}x{h}+{x}+{y}")
        self._listbox.delete(0, "end")
        for item in items:
            self._listbox.insert("end", item)

    def _close_popup(self, event=None):
        if self._popup is not None:
            self._popup.destroy()
            self._popup   = None
            self._listbox = None

    def _on_list_click(self, event=None):
        if self._listbox is None:
            return
        idx = self._listbox.nearest(event.y)
        if idx >= 0:
            self._pick(self._listbox.get(idx))

    def _on_list_focus_out(self, event=None):
        self.after(100, self._maybe_close_from_list)

    def _maybe_close_from_list(self):
        try:
            focused = self.focus_get()
        except Exception:
            focused = None
        if focused is not self._entry:
            self._close_popup()

    def _pick(self, value):
        self._close_popup()
        self._entry.delete(0, "end")
        self._entry.insert(0, value)
        self._block_next_open = True
        self._entry.focus_set()
        if self._on_change:
            self._on_change()


# ── Main App ──────────────────────────────────────────────────────────────────

class DRBFilterApp(tk.Tk):

    BG        = "#F4F5F7"
    PANEL_BG  = "#FFFFFF"
    ACCENT    = "#1B6B3A"
    ACCENT2   = "#2E86AB"
    LABEL_FG  = "#555770"
    TITLE_FG  = "#1A1D2E"
    SEP_COLOR = "#DDE1EC"
    RESULT_BG = "#FAFBFF"
    RESULT_FG = "#1A1D2E"
    HOVER_ADD = "#145228"
    HOVER_RST = "#1D6585"

    FONT_TITLE  = ("Segoe UI", 17, "bold")
    FONT_LABEL  = ("Segoe UI", 10)
    FONT_BTN    = ("Segoe UI", 10, "bold")
    FONT_RESULT = ("Consolas", 10)
    FONT_MSG    = ("Segoe UI", 10, "italic")

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.title("DRB Filter")
        self.configure(bg=self.BG)
        self.resizable(True, True)
        self.minsize(700, 440)
        self._build_styles()
        self._build_ui()
        self._center_window(820, 560)
        self._on_type_change()

    def _build_styles(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("App.TFrame",     background=self.BG)
        s.configure("Sep.TSeparator", background=self.SEP_COLOR)
        s.configure("Type.TCombobox",
                    fieldbackground="#FFFFFF", background="#FFFFFF",
                    foreground="#1A1D2E", arrowcolor=self.ACCENT,
                    selectbackground="#FFFFFF", selectforeground="#1A1D2E",
                    padding=(6, 4))
        s.map("Type.TCombobox",
              fieldbackground=[("readonly", "#FFFFFF")],
              selectbackground=[("readonly", "#FFFFFF")],
              selectforeground=[("readonly", "#1A1D2E")])

    def _build_ui(self):
        outer = ttk.Frame(self, style="App.TFrame", padding=16)
        outer.pack(fill="both", expand=True)

        card = tk.Frame(outer, bg=self.PANEL_BG,
                        highlightbackground=self.SEP_COLOR,
                        highlightthickness=1, bd=0)
        card.pack(fill="both", expand=True)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(6, weight=1)

        tk.Label(card, text="DRB Filter", bg=self.PANEL_BG,
                 fg=self.TITLE_FG, font=self.FONT_TITLE).grid(
            row=0, column=0, sticky="w", padx=20, pady=(18, 6))
        ttk.Separator(card, orient="horizontal",
                      style="Sep.TSeparator").grid(row=1, column=0, sticky="ew")

        fg = tk.Frame(card, bg=self.PANEL_BG)
        fg.grid(row=2, column=0, sticky="ew", padx=20, pady=14)
        fg.grid_columnconfigure(1, weight=1)
        fg.grid_columnconfigure(3, weight=1)

        self._lbl(fg, "Type:", 0, 0)
        self.type_var = tk.StringVar(value="Consumable")
        type_cb = ttk.Combobox(fg, textvariable=self.type_var,
                               values=["Consumable", "Solution"],
                               state="readonly", style="Type.TCombobox",
                               width=20, font=("Segoe UI", 10))
        type_cb.grid(row=0, column=1, sticky="w", pady=6)
        self.type_var.trace_add("write", lambda *_: self._on_type_change())

        self._lbl(fg, "Name:", 1, 0)
        self.name_field = DropdownField(fg, on_change=self._apply_filters)
        self.name_field.grid(row=1, column=1, sticky="ew", pady=6, padx=(0, 18), ipady=3)

        self._lbl(fg, "Code:", 1, 2)
        self.code_field = DropdownField(fg, on_change=self._apply_filters)
        self.code_field.grid(row=1, column=3, sticky="ew", pady=6, ipady=3)

        self._lbl(fg, "Material:", 2, 0)
        self.material_field = DropdownField(fg, on_change=self._apply_filters)
        self.material_field.grid(row=2, column=1, sticky="ew", pady=6, padx=(0, 18), ipady=3)

        self._lbl(fg, "Test:", 2, 2)
        self.test_field = DropdownField(fg, on_change=self._apply_filters)
        self.test_field.grid(row=2, column=3, sticky="ew", pady=6, ipady=3)

        ttk.Separator(card, orient="horizontal",
                      style="Sep.TSeparator").grid(row=3, column=0, sticky="ew")
        bb = tk.Frame(card, bg=self.PANEL_BG)
        bb.grid(row=4, column=0, sticky="ew", padx=20, pady=10)
        bb.grid_columnconfigure(0, weight=1)
        self._btn(bb, "+ Add",            self.ACCENT,  self.HOVER_ADD, self._on_add  ).grid(row=0, column=1, padx=(0, 8))
        self._btn(bb, "↺  Reset Filters", self.ACCENT2, self.HOVER_RST, self._on_reset).grid(row=0, column=2)

        ttk.Separator(card, orient="horizontal",
                      style="Sep.TSeparator").grid(row=5, column=0, sticky="ew")
        rf = tk.Frame(card, bg=self.PANEL_BG)
        rf.grid(row=6, column=0, sticky="nsew", padx=20, pady=(10, 18))
        rf.grid_columnconfigure(0, weight=1)
        rf.grid_rowconfigure(1, weight=1)

        tk.Label(rf, text="DRBs:", bg=self.PANEL_BG,
                 fg=self.LABEL_FG, font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, sticky="w")

        lf = tk.Frame(rf, bg=self.PANEL_BG)
        lf.grid(row=1, column=0, sticky="nsew")
        lf.grid_columnconfigure(0, weight=1)
        lf.grid_rowconfigure(0, weight=1)

        self.result_list = tk.Listbox(
            lf, font=self.FONT_RESULT, bg=self.RESULT_BG, fg=self.RESULT_FG,
            selectbackground=self.ACCENT, selectforeground="white",
            relief="flat", bd=0, activestyle="none",
            highlightthickness=1, highlightbackground=self.SEP_COLOR, height=6)
        self.result_list.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(lf, orient="vertical", command=self.result_list.yview)
        sb.grid(row=0, column=1, sticky="ns")
        self.result_list.configure(yscrollcommand=sb.set)

        self.status_label = tk.Label(
            rf, text="Apply filters to see matching DRBs",
            bg=self.PANEL_BG, fg="#9499B7", font=self.FONT_MSG)
        self.status_label.grid(row=1, column=0, sticky="w", pady=4)

    def _lbl(self, p, text, row, col):
        tk.Label(p, text=text, bg=self.PANEL_BG, fg=self.LABEL_FG,
                 font=("Segoe UI", 10)).grid(
            row=row, column=col, sticky="e", padx=(0, 8), pady=4)

    def _btn(self, p, text, color, hover, cmd):
        b = tk.Label(p, text=text, bg=color, fg="white", font=self.FONT_BTN,
                     padx=14, pady=6, cursor="hand2", relief="flat", bd=0)
        b.bind("<Button-1>", lambda e: cmd())
        b.bind("<Enter>",    lambda e: b.config(bg=hover))
        b.bind("<Leave>",    lambda e: b.config(bg=color))
        return b

    def _center_window(self, w, h):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _on_type_change(self):
        t = self.type_var.get()
        names, codes, materials, tests = get_all_options(self.db, t)
        self.name_field.set_all_values(names)
        self.code_field.set_all_values(codes)
        self.material_field.set_all_values(materials)
        self.test_field.set_all_values(tests)
        self.name_field.clear()
        self.code_field.clear()
        self.material_field.clear()
        self.test_field.clear()
        self._apply_filters()

    def _apply_filters(self):
        t    = self.type_var.get()
        name = self.name_field.get_value()
        code = self.code_field.get_value()
        mat  = self.material_field.get_value()
        test = self.test_field.get_value()

        result = filter_drbs(self.db, t, name, code, mat, test)
        self.result_list.delete(0, "end")

        if result is None:
            self.result_list.grid_remove()
            self.status_label.config(text="Apply filters to see matching DRBs")
            self.status_label.grid()
        elif len(result) == 0:
            self.result_list.grid_remove()
            self.status_label.config(text="no DRB matching")
            self.status_label.grid()
        else:
            self.status_label.grid_remove()
            for drb in result:
                self.result_list.insert("end", drb)
            self.result_list.grid()

    def _on_add(self):
        AddInstanceWindow(self)

    def _on_reset(self):
        self._on_type_change()

    def reload_db(self):
        """Reload db from Excel after a new row is added."""
        self.db = load_data()
        self._on_type_change()


# ── Add Instance Window ───────────────────────────────────────────────────────

class AddInstanceWindow(tk.Toplevel):
    """
    A separate window for adding a new row to the Excel database.
    Fields: DRB, Consumable Name, Consumable Code,
            Solution Name, Solution Code, Material, Test
    + Add Instance (green) and Cancel (red) buttons.
    """

    BG        = "#F4F5F7"
    PANEL_BG  = "#FFFFFF"
    ACCENT    = "#1B6B3A"
    DANGER    = "#C0392B"
    LABEL_FG  = "#555770"
    TITLE_FG  = "#1A1D2E"
    SEP_COLOR = "#DDE1EC"
    HOVER_ADD = "#145228"
    HOVER_CAN = "#922B21"
    ENTRY_BG  = "#FFFFFF"
    ENTRY_FG  = "#1A1D2E"
    BORDER    = "#C8CCDC"

    FONT_TITLE = ("Segoe UI", 17, "bold")
    FONT_LABEL = ("Segoe UI", 10)
    FONT_ENTRY = ("Segoe UI", 10)
    FONT_BTN   = ("Segoe UI", 10, "bold")

    FIELDS = [
        ("DRB",              "DRB"),
        ("Consumable Name:", "Consumable_Name"),
        ("Consumable Code:", "Consumable_Code"),
        ("Solution Name:",   "Solution_Name"),
        ("Solution Code:",   "Solution_Code"),
        ("Material:",        "Material"),
        ("Test:",            "Test"),
    ]

    def __init__(self, parent):
        super().__init__(parent)
        self._parent = parent
        self.title("Add New Instance")
        self.configure(bg=self.BG)
        self.resizable(False, False)
        self.grab_set()   # modal

        self._entries = {}
        self._build_ui()
        self._center(560, 480)

    def _build_ui(self):
        outer = tk.Frame(self, bg=self.BG, padx=16, pady=16)
        outer.pack(fill="both", expand=True)

        card = tk.Frame(outer, bg=self.PANEL_BG,
                        highlightbackground=self.SEP_COLOR,
                        highlightthickness=1, bd=0)
        card.pack(fill="both", expand=True)

        # Title
        tk.Label(card, text="Add New Instance", bg=self.PANEL_BG,
                 fg=self.TITLE_FG, font=self.FONT_TITLE).pack(
            anchor="w", padx=20, pady=(18, 6))

        ttk.Separator(card, orient="horizontal").pack(fill="x")

        # Form
        form = tk.Frame(card, bg=self.PANEL_BG)
        form.pack(fill="x", padx=30, pady=16)
        form.grid_columnconfigure(1, weight=1)

        for i, (label, key) in enumerate(self.FIELDS):
            tk.Label(form, text=label, bg=self.PANEL_BG,
                     fg=self.LABEL_FG, font=self.FONT_LABEL,
                     anchor="e").grid(row=i, column=0, sticky="e",
                                      padx=(0, 10), pady=5)

            border = tk.Frame(form, bg=self.BORDER, padx=1, pady=1)
            border.grid(row=i, column=1, sticky="ew", pady=5)

            entry = tk.Entry(border, font=self.FONT_ENTRY,
                             bg=self.ENTRY_BG, fg=self.ENTRY_FG,
                             relief="flat", bd=4, highlightthickness=0)
            entry.pack(fill="both", expand=True)
            self._entries[key] = entry

        ttk.Separator(card, orient="horizontal").pack(fill="x", pady=(8, 0))

        # Buttons
        bb = tk.Frame(card, bg=self.PANEL_BG)
        bb.pack(fill="x", padx=20, pady=12)

        self._btn(bb, "+ Add Instance", self.ACCENT,  self.HOVER_ADD, self._on_add_instance).pack(side="left", padx=(0, 8))
        self._btn(bb, "✕ Cancel",       self.DANGER,  self.HOVER_CAN, self._on_cancel     ).pack(side="left")

    def _btn(self, parent, text, color, hover, cmd):
        b = tk.Label(parent, text=text, bg=color, fg="white",
                     font=self.FONT_BTN, padx=14, pady=7,
                     cursor="hand2", relief="flat", bd=0)
        b.bind("<Button-1>", lambda e: cmd())
        b.bind("<Enter>",    lambda e: b.config(bg=hover))
        b.bind("<Leave>",    lambda e: b.config(bg=color))
        return b

    def _center(self, w, h):
        self.update_idletasks()
        px = self._parent.winfo_x() + (self._parent.winfo_width()  - w) // 2
        py = self._parent.winfo_y() + (self._parent.winfo_height() - h) // 2
        self.geometry(f"{w}x{h}+{px}+{py}")

    def _on_add_instance(self):
        new_row = {}
        for key, entry in self._entries.items():
            val = entry.get().strip()
            new_row[key] = val if val else ""

        # Must have at least a DRB value
        if not new_row.get("DRB"):
            messagebox.showwarning("Missing Field", "DRB field cannot be empty.",
                                   parent=self)
            return

        try:
            # Read current Excel, append row, save
            df = pd.read_excel(EXCEL_FILE, dtype=str).fillna("")
            new_df = pd.DataFrame([new_row])
            df = pd.concat([df, new_df], ignore_index=True)
            df.to_excel(EXCEL_FILE, index=False, sheet_name="Sheet1")
        except Exception as e:
            messagebox.showerror("Save Error", str(e), parent=self)
            return

        # Reload parent db and refresh filters
        self._parent.reload_db()
        self.destroy()

    def _on_cancel(self):
        self.destroy()


# ── Splash Screen ─────────────────────────────────────────────────────────────

class SplashScreen(tk.Tk):

    BG       = "#FFFFFF"
    ACCENT   = "#1B6B3A"
    TITLE_FG = "#1A1D2E"
    LABEL_FG = "#9499B7"
    SEP_COLOR= "#DDE1EC"

    FONT_TITLE  = ("Segoe UI", 15, "bold")
    FONT_STATUS = ("Segoe UI", 9)

    STEPS = [
        "Reading database...",
        "Loading Excel file...",
        "Processing records...",
        "Building index...",
    ]

    def __init__(self):
        super().__init__()
        self.overrideredirect(True)          # title bar yok
        self.configure(bg=self.SEP_COLOR)
        self.resizable(False, False)
        self.wm_attributes("-topmost", True)

        self._pct    = 0
        self._step   = 0

        self._build_ui()
        self._center(340, 140)
        self.update()

    def _build_ui(self):
        inner = tk.Frame(self, bg=self.BG, padx=28, pady=22)
        inner.pack(fill="both", expand=True, padx=1, pady=1)

        tk.Label(inner, text="DRB Filter", bg=self.BG,
                 fg=self.TITLE_FG, font=self.FONT_TITLE).pack(anchor="w")

        self._status_var = tk.StringVar(value="Starting...")
        tk.Label(inner, textvariable=self._status_var, bg=self.BG,
                 fg=self.LABEL_FG, font=self.FONT_STATUS).pack(anchor="w", pady=(2, 10))

        # Progress bar track
        track = tk.Frame(inner, bg=self.SEP_COLOR, height=5)
        track.pack(fill="x")
        track.pack_propagate(False)

        self._bar = tk.Frame(track, bg=self.ACCENT, height=5, width=0)
        self._bar.place(x=0, y=0, relheight=1.0)

        self._track = track

    def _center(self, w, h):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def set_status(self, text, pct):
        """Update status text and progress bar percentage."""
        self._status_var.set(text)
        self._pct = pct
        track_w = self._track.winfo_width()
        bar_w   = max(0, int(track_w * pct / 100))
        self._bar.place(x=0, y=0, relheight=1.0, width=bar_w)
        self.update()


if __name__ == "__main__":
    try:
        splash = SplashScreen()

        splash.set_status("Reading database...",    20)
        splash.set_status("Loading Excel file...",  45)
        db = load_data()

        splash.set_status("Processing records...",  75)
        splash.set_status("Building index...",      95)
        splash.set_status("Done!",                 100)

        splash.after(200, splash.destroy)
        splash.mainloop()

        app = DRBFilterApp(db)
        app.mainloop()

    except KeyboardInterrupt:
        pass
    except Exception as e:
        try:
            messagebox.showerror("Error", str(e))
        except Exception:
            pass
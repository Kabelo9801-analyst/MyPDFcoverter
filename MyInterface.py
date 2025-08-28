
#!/usr/bin/env python3
"""
Modern GUI for Doc Converter using ttkbootstrap.
"""
import os, sys, subprocess, threading, queue, platform
from pathlib import Path
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from tkinter import filedialog
from dotenv import load_dotenv
load_dotenv()


try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except Exception:
    DND_AVAILABLE = False

HERE = Path(__file__).resolve().parent

def run_converter_async(inp, outp, model, formats, workers, log_q):
    py = sys.executable
    script = str(HERE / "legal_converter.py")
    cmd = [py, script, "--input", inp, "--output", outp, "--model", model, "--formats", formats, "--workers", str(workers)]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in iter(proc.stdout.readline, ""):
            log_q.put(line.rstrip("\n"))
        code = proc.wait()
        log_q.put(f"\\n[done] Exit code: {code}")
    except Exception as e:
        log_q.put(f"[error] {e}")

class App(tb.Window if not DND_AVAILABLE else TkinterDnD.Tk):  # type: ignore[misc]
    def __init__(self, themename="cyborg"):
        if DND_AVAILABLE:
            super().__init__(); tb.Style(theme=themename)
        else:
            super().__init__(themename=themename)
        self.title("Legal Converter — Modern GUI")
        self.geometry("940x640"); self.minsize(860, 560)
        self.log_q = queue.Queue()
        self._build_ui(); self._poll_log()
        self.selected_theme = themename

    def _build_ui(self):
        header = tb.Frame(self, padding=16); header.pack(side=TOP, fill=X)
        tb.Label(header, text="Kabelo's Tax Consulting Doc App", font=("Inter", 20, "bold")).pack(anchor="w")
        tb.Label(header, text="Plain-English & Bullet Summary ", bootstyle="secondary").pack(anchor="w", pady=(2,0))

        body = tb.Frame(self, padding=(16,0,16,16)); body.pack(fill=BOTH, expand=YES)

        left = tb.Labelframe(body, text=" Settings ", padding=14, bootstyle="secondary")
        left.pack(side=LEFT, fill=Y, padx=(0,12))

        self.in_var = tb.StringVar(); self._entry_with_browse(left, "Input folder", self.in_var, self._choose_in).pack(fill=X, pady=4)
        self.out_var = tb.StringVar(); self._entry_with_browse(left, "Output folder", self.out_var, self._choose_out).pack(fill=X, pady=4)
        self.model_var = tb.StringVar(value="gpt-4o-mini"); self._entry_with_label(left, "LLM Model", self.model_var).pack(fill=X, pady=4)
        self.formats_var = tb.StringVar(value="docx,pdf"); self._entry_with_label(left, "Output formats (comma)", self.formats_var).pack(fill=X, pady=4)

        self.workers_var = tb.IntVar(value=3)
        row = tb.Frame(left); tb.Label(row, text="Parallel workers").pack(side=LEFT)
        tb.Spinbox(row, from_=1, to=16, textvariable=self.workers_var, width=6, bootstyle="info").pack(side=LEFT, padx=8); row.pack(fill=X, pady=4)

        theme_row = tb.Frame(left); tb.Label(theme_row, text="Theme").pack(side=LEFT)
        self.theme_combo = tb.Combobox(theme_row, values=tb.Style().theme_names(), state="readonly", width=18)
        self.theme_combo.set("cyborg"); self.theme_combo.bind("<<ComboboxSelected>>", self._on_theme_change); self.theme_combo.pack(side=LEFT, padx=8); theme_row.pack(fill=X, pady=(6,10))

        btn_row = tb.Frame(left)
        self.run_btn = tb.Button(btn_row, text="▶ Run Conversion", command=self._on_run, bootstyle=SUCCESS); self.run_btn.pack(side=LEFT)
        tb.Button(btn_row, text="🧪 Test Setup", command=self._on_validate, bootstyle=INFO).pack(side=LEFT, padx=8); btn_row.pack(anchor="w", pady=(6,2))

        # API status label (now backed by _api_status_text)
        self.api_lbl = tb.Label(left, text=self._api_status_text(), bootstyle="warning"); self.api_lbl.pack(anchor="w", pady=(6,2))

        if DND_AVAILABLE and platform.system() != "Windows":
            tb.Label(left, text="Tip: Drag folders into the log panel", bootstyle="secondary").pack(anchor="w", pady=(6,2))

        right = tb.Labelframe(body, text=" Live Log ", padding=12, bootstyle="secondary"); right.pack(side=LEFT, fill=BOTH, expand=YES)
        from ttkbootstrap.scrolled import ScrolledText
        self.log = ScrolledText(right, autohide=True, height=22, padding=2, bootstyle="dark"); self.log.pack(fill=BOTH, expand=YES)

        if DND_AVAILABLE and platform.system() != "Windows":
            try:
                from tkinterdnd2 import DND_FILES
                self.log.drop_target_register(DND_FILES)
                self.log.dnd_bind("<<Drop>>", self._on_drop)
            except Exception:
                pass

        footer = tb.Frame(self, padding=10); footer.pack(side=BOTTOM, fill=X)
        self.status = tb.Label(footer, text="Ready", bootstyle="secondary"); self.status.pack(side=LEFT)
        tb.Button(footer, text="Clear Log", command=lambda: self.log.delete("1.0", "end"), bootstyle=SECONDARY).pack(side=RIGHT)

        self.bind("<Return>", lambda e: self._on_run())
        self.bind("<Control-l>", lambda e: self.log.delete("1.0", "end"))

    # --- NEW: API status helper
    def _api_status_text(self):
        return "✅ API key detected" if os.getenv("OPENAI_API_KEY") else "⚠️ API key missing (.env or environment)"

    def _entry_with_browse(self, parent, label, var, callback):
        row = tb.Frame(parent); tb.Label(row, text=label).pack(side=LEFT)
        tb.Entry(row, textvariable=var, width=34).pack(side=LEFT, padx=8)
        tb.Button(row, text="Browse…", command=callback, bootstyle=PRIMARY).pack(side=LEFT); return row

    def _entry_with_label(self, parent, label, var):
        row = tb.Frame(parent); tb.Label(row, text=label).pack(side=LEFT)
        tb.Entry(row, textvariable=var, width=34).pack(side=LEFT, padx=8); return row

    def _choose_in(self):
        d = filedialog.askdirectory(title="Select Input Folder"); 
        if d: self.in_var.set(d)

    def _choose_out(self):
        d = filedialog.askdirectory(title="Select Output Folder");
        if d: self.out_var.set(d)

    def _on_theme_change(self, _):
        new_theme = self.theme_combo.get(); tb.Style().theme_use(new_theme)
        self.selected_theme = new_theme; self._toast("Theme switched", f"Theme set to: {new_theme}", duration=2000)

    def _on_validate(self):
        problems = []
        if not (HERE / "legal_converter.py").exists(): problems.append("legal_converter.py not found next to this GUI.")
        if not os.getenv("OPENAI_API_KEY"): problems.append("OPENAI_API_KEY is not set (consider .env + python-dotenv).")
        if not self.in_var.get(): problems.append("Input folder not selected.")
        if not self.out_var.get(): problems.append("Output folder not selected.")
        # Refresh API label dynamically:
        self.api_lbl.config(text=self._api_status_text())
        if problems: self._toast("Setup issues", "\n".join(problems), bootstyle="danger")
        else: self._toast("All good", "Environment and paths look OK!", bootstyle="success")

    def _on_run(self):
        inp, outp = self.in_var.get().strip(), self.out_var.get().strip()
        model, formats, workers = self.model_var.get().strip(), self.formats_var.get().strip(), self.workers_var.get()
        if not inp or not outp: self._toast("Missing folders", "Select both input and output folders.", bootstyle="danger"); return
        if not os.getenv("OPENAI_API_KEY"): self._toast("API key missing", "Set OPENAI_API_KEY and try again.", bootstyle="warning"); return
        self.run_btn.config(state=DISABLED); self.status.config(text="Running…")
        self.log.delete("1.0", "end"); self.log.insert("end", f"▶ Running converter\nInput: {inp}\nOutput: {outp}\nModel: {model}\nFormats: {formats}\nWorkers: {workers}\n\n")
        threading.Thread(target=run_converter_async, args=(inp, outp, model, formats, workers, self.log_q), daemon=True).start()

    def _poll_log(self):
        try:
            while True:
                line = self.log_q.get_nowait()
                if line.startswith("[done]"):
                    self.status.config(text="Finished"); self.run_btn.config(state=NORMAL)
                    self._toast("Conversion finished", line, bootstyle="success")
                elif line.startswith("[error]"):
                    self.status.config(text="Error"); self.run_btn.config(state=NORMAL); self._toast("Error", line, bootstyle="danger")
                else:
                    self.log.insert("end", line + "\n"); self.log.see("end")
        except queue.Empty:
            pass
        finally:
            self.after(120, self._poll_log)

    def _on_drop(self, event):
        try:
            paths = self.tk.splitlist(event.data)
        except Exception:
            paths = []
        if not paths: return
        p = Path(paths[0])
        if p.is_dir(): self.in_var.set(str(p)); self._toast("Input set", str(p))
        else: self._toast("Drop a folder", "Please drop a folder, not a file.", bootstyle="warning")

    def _toast(self, title, message, duration=2500, bootstyle="info"):
        ToastNotification(title=title, message=message, duration=duration, bootstyle=bootstyle, position=(None, 64, "ne")).show()

if __name__ == "__main__":
    app = App(themename="cyborg"); app.mainloop()

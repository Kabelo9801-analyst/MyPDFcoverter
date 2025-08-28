
#!/usr/bin/env python3
"""
legal_converter_gui.py — Minimal GUI (Tkinter) to run legal_converter.py
"""
import os, sys, subprocess, threading, tkinter as tk
from tkinter import ttk, filedialog, messagebox

HERE = os.path.dirname(os.path.abspath(__file__))

def run_converter(inp, outp, model, formats, workers):
    py = sys.executable
    script = os.path.join(HERE, "legal_converter.py")
    cmd = [py, script, "--input", inp, "--output", outp, "--formats", formats, "--workers", str(workers)]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kabelo's Doc Converter —")
        self.geometry("720x520")

        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Input folder:").grid(row=0, column=0, sticky="w")
        self.input_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.input_var, width=60).grid(row=0, column=1, sticky="we")
        ttk.Button(frm, text="Browse...", command=self.browse_input).grid(row=0, column=2, padx=5)

        ttk.Label(frm, text="Output folder:").grid(row=1, column=0, sticky="w")
        self.output_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.output_var, width=60).grid(row=1, column=1, sticky="we")
        ttk.Button(frm, text="Browse...", command=self.browse_output).grid(row=1, column=2, padx=5)

        ttk.Label(frm, text="Model:").grid(row=2, column=0, sticky="w")
        self.model_var = tk.StringVar(value="gpt-4o-mini")
        ttk.Entry(frm, textvariable=self.model_var, width=30).grid(row=2, column=1, sticky="w")

        ttk.Label(frm, text="Output formats (comma):").grid(row=3, column=0, sticky="w")
        self.formats_var = tk.StringVar(value="docx,txt")
        ttk.Entry(frm, textvariable=self.formats_var, width=30).grid(row=3, column=1, sticky="w")

        ttk.Label(frm, text="Parallel workers:").grid(row=4, column=0, sticky="w")
        self.workers_var = tk.IntVar(value=3)
        ttk.Spinbox(frm, from_=1, to=16, textvariable=self.workers_var, width=10).grid(row=4, column=1, sticky="w")

        self.run_btn = ttk.Button(frm, text="Run Conversion", command=self.on_run)
        self.run_btn.grid(row=5, column=1, pady=8, sticky="w")

        self.log = tk.Text(frm, height=18, wrap="word")
        self.log.grid(row=6, column=0, columnspan=3, sticky="nsew", pady=(8,0))

        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(6, weight=1)

    def browse_input(self):
        d = filedialog.askdirectory(title="Select Input Folder")
        if d: self.input_var.set(d)

    def browse_output(self):
        d = filedialog.askdirectory(title="Select Output Folder")
        if d: self.output_var.set(d)

    def on_run(self):
        inp = self.input_var.get().strip()
        outp = self.output_var.get().strip()
        model = self.model_var.get().strip()
        formats = self.formats_var.get().strip()
        workers = self.workers_var.get()

        if not inp or not outp:
            messagebox.showerror("Missing folders", "Please select both input and output folders."); return
        if not os.getenv("OPENAI_API_KEY"):
            messagebox.showwarning("API key missing", "OPENAI_API_KEY is not set. Set it in your environment first."); return

        self.run_btn.config(state="disabled")
        self.log.delete("1.0", "end")
        self.log.insert("end", f"Running...\nInput: {inp}\nOutput: {outp}\nModel: {model}\nFormats: {formats}\nWorkers: {workers}\n\n")

        def worker():
            proc = run_converter(inp, outp, model, formats, workers)
            for line in proc.stdout:
                self.log.insert("end", line); self.log.see("end")
            code = proc.wait()
            self.log.insert("end", f"\nFinished with exit code {code}\n")
            self.run_btn.config(state="normal")
        threading.Thread(target=worker, daemon=True).start()

if __name__ == "__main__":
    App().mainloop()

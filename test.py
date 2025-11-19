

import tkinter as tk
from tkinter import scrolledtext
import clips

RULES = r"""
(defmodule MAIN)

;; Rule 1: Severe COVID-19 warning (urgent care recommended)
(defrule covid-severe-rule
    (has shortness-of-breath)
    (or (has chest-pain) (has persistent-high-fever))
    =>
    (assert (diagnosis covid-severe)))

;; Rule 2: Suspected COVID-19
(defrule covid-suspected-rule
    (has fever)
    (has dry-cough)
    (has loss-smell)
    =>
    (assert (diagnosis covid-suspected)))

;; Fallback: unknown when no diagnosis facts asserted
(defrule unknown-rule
    (not (diagnosis ?))
    =>
    (assert (diagnosis unknown)))
"""


class CovidExpertSystemApp:
    def __init__(self, master):
        self.master = master
        master.title("COVID-19 Diagnosis Expert System (Toy)")
        master.geometry("560x460")

        self.symptoms = [
            ("Fever", "fever"),
            ("Persistent high fever (subjective)", "persistent-high-fever"),
            ("Dry cough", "dry-cough"),
            ("Loss of smell or taste", "loss-smell"),
            ("Shortness of breath", "shortness-of-breath"),
            ("Chest pain or pressure", "chest-pain"),
            ("Sore throat", "sore-throat"),
            ("Runny nose / Sneezing", "runny-nose"),
        ]

        self.vars = {}
        label = tk.Label(master, text="Select symptoms you are experiencing:", font=(None, 12, 'bold'))
        label.grid(row=0, column=0, sticky="w", padx=10, pady=(10,4))

        for i, (text, key) in enumerate(self.symptoms, start=1):
            var = tk.IntVar(value=0)
            cb = tk.Checkbutton(master, text=text, variable=var)
            cb.grid(row=i, column=0, sticky="w", padx=20)
            self.vars[key] = var

        # Control buttons
        btn_frame = tk.Frame(master)
        btn_frame.grid(row=1, column=1, rowspan=6, padx=10, pady=10, sticky="n")

        diagnose_btn = tk.Button(btn_frame, text="Diagnose", width=16, command=self.diagnose)
        diagnose_btn.pack(pady=(10, 6))

        explain_btn = tk.Button(btn_frame, text="Show rulebook", width=16, command=self.show_rules)
        explain_btn.pack(pady=6)

        clear_btn = tk.Button(btn_frame, text="Clear", width=16, command=self.clear)
        clear_btn.pack(pady=6)

        quit_btn = tk.Button(btn_frame, text="Quit", width=16, command=master.quit)
        quit_btn.pack(pady=6)

        # Results text box
        self.output = scrolledtext.ScrolledText(master, width=70, height=12, wrap=tk.WORD)
        self.output.grid(row=10, column=0, columnspan=2, padx=10, pady=(8,10))
        self.output.insert(tk.END, "Ready. Select symptoms and press Diagnose.\n")
        self.output.configure(state='disabled')

        # CLIPS environment
        self.env = clips.Environment()

    def _build_rules(self):
        try:
            self.env.clear()
        except Exception:
            self.env = clips.Environment()
        self.env.build(RULES)

    def _assert_symptoms(self):
        for key, var in self.vars.items():
            if var.get():
                fact_str = f"(has {key})"
                try:
                    self.env.assert_string(fact_str)
                except Exception as e:
                    print("Error asserting fact:", e)

    def _collect_diagnoses(self):
        # Run the engine
        self.env.run()
        diags = []
        for fact in self.env.facts():
            s = str(fact).strip()
            if s.startswith('(diagnosis') or 'diagnosis' in s:
                parts = s.replace('(', '').replace(')', '').split()
                try:
                    idx = parts.index('diagnosis')
                    if idx + 1 < len(parts):
                        diags.append(parts[idx + 1])
                except ValueError:
                    continue
        # preserve order, unique
        seen = set()
        unique = []
        for d in diags:
            if d not in seen:
                unique.append(d)
                seen.add(d)
        return unique

    def diagnose(self):
        self._build_rules()
        self._assert_symptoms()
        diagnoses = self._collect_diagnoses()

        self.output.configure(state='normal')
        self.output.delete('1.0', tk.END)

        if diagnoses:
            if diagnoses == ['unknown']:
                self.output.insert(tk.END, "No clear COVID-19 related diagnosis found based on selected symptoms.\n")
                self.output.insert(tk.END, "If you suspect infection or symptoms worsen, get tested and consult a healthcare professional.\n")
            else:
                for d in diagnoses:
                    if d == 'covid-severe':
                        self.output.insert(tk.END, "Diagnosis: POTENTIAL SEVERE COVID-19 (or other severe respiratory condition)\n")
                        self.output.insert(tk.END, "-- Advice: Seek urgent medical care or call emergency services.\n\n")
                    elif d == 'covid-suspected':
                        self.output.insert(tk.END, "Diagnosis: COVID-19 SUSPECTED\n")
                        self.output.insert(tk.END, "-- Advice: Self-isolate, get tested (PCR/antigen), monitor symptoms, and consult healthcare services.\n\n")
                    else:
                        self.output.insert(tk.END, f"Diagnosis: {d}\n")
                self.output.insert(tk.END, "Note: This is a teaching/demo system — not medical advice.\n")
        else:
            self.output.insert(tk.END, "Engine returned no diagnosis facts.\n")

        self.output.configure(state='disabled')

    def show_rules(self):
        # Present a short summary of the 2 rules (non-technical)
        msg = (
            "Rule 1 (covid-severe): shortness-of-breath AND (chest pain OR persistent high fever) -> covid-severe\n\n"
            "Rule 2 (covid-suspected): fever AND dry cough AND loss of smell/taste -> covid-suspected\n\n"
            "Fallback: if no rule applies -> unknown\n\n"
            "Reminder: This is an educational toy. For health emergencies, contact healthcare services immediately."
        )
        self.output.configure(state='normal')
        self.output.delete('1.0', tk.END)
        self.output.insert(tk.END, msg)
        self.output.configure(state='disabled')

    def clear(self):
        for var in self.vars.values():
            var.set(0)
        self.output.configure(state='normal')
        self.output.delete('1.0', tk.END)
        self.output.insert(tk.END, "Selections cleared. Ready.\n")
        self.output.configure(state='disabled')


if __name__ == '__main__':
    root = tk.Tk()
    app = CovidExpertSystemApp(root)
    root.mainloop()

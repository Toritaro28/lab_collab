import tkinter as tk
from tkinter import ttk, messagebox
import clips

class ModernExpertSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced COVID-19 & Respiratory Expert System")
        self.root.geometry("700x750")
        
        # Apply a theme
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Header.TLabel", font=("Helvetica", 14, "bold"), foreground="#333")
        self.style.configure("Question.TLabel", font=("Helvetica", 11))
        self.style.configure("TButton", font=("Helvetica", 10, "bold"))

        # --- Data Storage ---
        # Dictionary to hold the Tkinter variables
        self.vars = {
            "fever": tk.StringVar(value="no"),
            "cough": tk.StringVar(value="no"),
            "breathing": tk.StringVar(value="no"),
            "sore_throat": tk.StringVar(value="no"),
            "taste_smell": tk.StringVar(value="no"),
            "body_ache": tk.StringVar(value="no"),
            "pre_existing": tk.StringVar(value="no"), # Diabetes, Asthma, etc.
            "contact": tk.StringVar(value="no"), # Contact with infected person
        }
        self.age_var = tk.StringVar()
        self.name_var = tk.StringVar()

        # --- Initialize CLIPS ---
        self.env = clips.Environment()
        self.init_knowledge_base()

        # --- Build UI ---
        self.create_ui()

    def init_knowledge_base(self):
        """
        Defines the Knowledge Base: Templates and Rules.
        Using a 'Risk Score' logic which is more robust than simple If-Then.
        """
        self.env.clear()

        # 1. Templates
        self.env.build("(deftemplate patient (slot name) (slot age))")
        self.env.build("(deftemplate symptom (slot id) (slot val))")
        # A generic 'advice' fact to accumulate reasons
        self.env.build("(deftemplate advice (slot type) (slot message))")
        
        # 2. Rules
        
        # --- Rule: Critical Emergency ---
        # Difficulty breathing overrides almost everything
        rule_emergency = """
        (defrule emergency-check
            (symptom (id "breathing") (val "yes"))
            =>
            (assert (advice (type "critical") (message "CRITICAL: Difficulty breathing is a severe symptom.")))
            (assert (diagnosis_level 100))
        )
        """

        # --- Rule: High Likelihood (The 'Classic' Covid Combo) ---
        rule_covid_classic = """
        (defrule classic-covid
            (symptom (id "fever") (val "yes"))
            (symptom (id "cough") (val "yes"))
            (symptom (id "taste_smell") (val "yes"))
            =>
            (assert (advice (type "warning") (message "High Probability: Loss of taste/smell with fever is highly specific to COVID-19.")))
            (assert (diagnosis_level 80))
        )
        """

        # --- Rule: Risk Factors (Age > 60) ---
        rule_age_risk = """
        (defrule risk-age
            (patient (age ?a&:(>= ?a 60)))
            =>
            (assert (advice (type "risk") (message "Risk Factor: Patient is over 60, requiring extra caution.")))
            (assert (risk_adder 20))
        )
        """

        # --- Rule: Risk Factors (Pre-existing conditions) ---
        rule_condition_risk = """
        (defrule risk-conditions
            (symptom (id "pre_existing") (val "yes"))
            =>
            (assert (advice (type "risk") (message "Risk Factor: Pre-existing medical conditions detected.")))
            (assert (risk_adder 20))
        )
        """

        # --- Rule: Contact History ---
        rule_contact = """
        (defrule contact-tracing
            (symptom (id "contact") (val "yes"))
            =>
            (assert (advice (type "warning") (message "Exposure: Known contact with a confirmed case.")))
            (assert (diagnosis_level 50)) 
        )
        """

        # --- Rule: Common Cold / Flu ---
        rule_flu = """
        (defrule flu-check
            (symptom (id "fever") (val "yes"))
            (symptom (id "body_ache") (val "yes"))
            (symptom (id "breathing") (val "no"))
            (symptom (id "taste_smell") (val "no"))
            =>
            (assert (advice (type "info") (message "Analysis: Symptoms resemble seasonal Flu.")))
            (assert (diagnosis_level 30))
        )
        """

        # Build all rules
        self.env.build(rule_emergency)
        self.env.build(rule_covid_classic)
        self.env.build(rule_age_risk)
        self.env.build(rule_condition_risk)
        self.env.build(rule_contact)
        self.env.build(rule_flu)

    def create_ui(self):
        # Main Container with Scrollbar (in case screen is small)
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Section 1: Patient Info ---
        info_frame = ttk.LabelFrame(self.scrollable_frame, text=" Patient Information ", padding=15)
        info_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(info_frame, text="Full Name:", style="Question.TLabel").grid(row=0, column=0, padx=5, sticky="w")
        ttk.Entry(info_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, padx=5)

        ttk.Label(info_frame, text="Age:", style="Question.TLabel").grid(row=0, column=2, padx=5, sticky="w")
        ttk.Entry(info_frame, textvariable=self.age_var, width=10).grid(row=0, column=3, padx=5)

        # --- Section 2: Symptoms ---
        symptom_frame = ttk.LabelFrame(self.scrollable_frame, text=" Clinical Symptoms ", padding=15)
        symptom_frame.pack(fill="x", padx=20, pady=10)

        self.create_row(symptom_frame, 0, "Do you have a fever (over 38°C)?", "fever")
        self.create_row(symptom_frame, 1, "Do you have a continuous dry cough?", "cough")
        self.create_row(symptom_frame, 2, "Do you have difficulty breathing?", "breathing")
        self.create_row(symptom_frame, 3, "Do you have a sore throat?", "sore_throat")
        self.create_row(symptom_frame, 4, "Loss of taste or smell?", "taste_smell")
        self.create_row(symptom_frame, 5, "Severe body aches / fatigue?", "body_ache")

        # --- Section 3: Risk Factors ---
        risk_frame = ttk.LabelFrame(self.scrollable_frame, text=" Risk Factors & History ", padding=15)
        risk_frame.pack(fill="x", padx=20, pady=10)

        self.create_row(risk_frame, 0, "Pre-existing conditions (Asthma, Diabetes, Heart)?", "pre_existing")
        self.create_row(risk_frame, 1, "Contact with known COVID-19 case?", "contact")

        # --- Section 4: Controls ---
        btn_frame = ttk.Frame(self.scrollable_frame)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="Analyze Symptoms", command=self.run_diagnosis, width=20).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Reset Form", command=self.reset_form, width=20).pack(side="left", padx=10)

        # --- Section 5: Explanation Facility (The Log) ---
        log_frame = ttk.LabelFrame(self.scrollable_frame, text=" Expert System Reasoning ", padding=15)
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.log_text = tk.Text(log_frame, height=10, width=70, state="disabled", bg="#f0f0f0", font=("Consolas", 10))
        self.log_text.pack(fill="both", expand=True)

    def create_row(self, parent, row, text, var_key):
        """Helper to create a nice Yes/No row"""
        ttk.Label(parent, text=text, style="Question.TLabel").grid(row=row, column=0, padx=10, pady=5, sticky="w")
        
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=1, padx=10, pady=5, sticky="e")
        
        ttk.Radiobutton(frame, text="Yes", variable=self.vars[var_key], value="yes").pack(side="left", padx=5)
        ttk.Radiobutton(frame, text="No", variable=self.vars[var_key], value="no").pack(side="left", padx=5)

    def log(self, message):
        """Update the text area with reasoning"""
        self.log_text.config(state="normal")
        self.log_text.insert("end", ">> " + message + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, "end")
        self.log_text.config(state="disabled")

    def reset_form(self):
        for key in self.vars:
            self.vars[key].set("no")
        self.name_var.set("")
        self.age_var.set("")
        self.clear_log()

    def run_diagnosis(self):
        # 1. Validation
        try:
            age = int(self.age_var.get())
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid Age.")
            return
        
        name = self.name_var.get()
        if not name: 
            name = "Patient"

        self.clear_log()
        self.log(f"Starting inference for {name}, Age: {age}...")

        # 2. Reset CLIPS and Load Rules (Reloading ensures clean state)
        self.init_knowledge_base()
        self.env.reset()

        # 3. Assert Facts (Insert Data into Expert System)
        # Patient Fact
        self.env.assert_string(f'(patient (name "{name}") (age {age}))')

        # Symptom Facts
        for key, var in self.vars.items():
            # We assert the fact: (symptom (id "fever") (val "yes"))
            self.env.assert_string(f'(symptom (id "{key}") (val "{var.get()}"))')

        # 4. Run Inference
        self.env.run()

        # 5. Collect Results
        # We calculate a 'score' based on the facts generated by the rules
        base_score = 0
        reasons = []
        critical = False

        for fact in self.env.facts():
            template_name = fact.template.name
            
            if template_name == 'advice':
                msg_type = fact['type']
                message = fact['message']
                reasons.append(f"[{msg_type.upper()}] {message}")
                
            elif template_name == 'diagnosis_level':
                # Logic: Take the highest diagnosis level found
                lvl = int(fact[0])
                if lvl > base_score:
                    base_score = lvl
            
            elif template_name == 'risk_adder':
                # Logic: Add to the base score
                base_score += int(fact[0])

        # 6. Final Decision Logic (Python handles the final UI presentation based on ES data)
        self.log(f"Inference Complete. Calculated Risk Score: {base_score}")
        for r in reasons:
            self.log(r)

        # Show Popup Result
        if base_score >= 100:
            messagebox.showwarning("Result", "HIGH RISK / EMERGENCY\nPlease go to the nearest hospital immediately.\nCheck the logs for details.")
        elif base_score >= 60:
            messagebox.showwarning("Result", "MODERATE to HIGH RISK\nYou have significant symptoms. Isolate and consult a doctor.")
        elif base_score >= 30:
            messagebox.showinfo("Result", "LOW to MODERATE RISK\nLikely a Flu or Cold, but monitor your symptoms closely.")
        else:
            messagebox.showinfo("Result", "LOW RISK\nYou appear healthy or have very mild symptoms.")

# --- Main Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = ModernExpertSystem(root)
    root.mainloop()
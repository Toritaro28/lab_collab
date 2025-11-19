import tkinter as tk
from tkinter import messagebox
import clips

class CovidExpertSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("COVID-19 Diagnosis Expert System")

        # Initialize the CLIPS environment
        self.env = clips.Environment()

        # Define the corrected rules with simplified fact patterns
        rule1 = """
        (defrule high-risk
            (symptom fever)
            (symptom cough)
            (symptom shortness-of-breath)
            =>
            (assert (result "High Risk")))
        """
        rule2 = """
        (defrule possible-risk
            (contact-with-confirmed-case yes)
            (or (symptom fever)
                (symptom cough)
                (symptom shortness-of-breath))
            =>
            (assert (result "Possible Risk")))
        """

        # Build the rules in the CLIPS environment
        self.env.build(rule1)
        self.env.build(rule2)

        # Define the questions for the user interface
        self.questions = {
            "fever": "Do you have a fever?",
            "cough": "Do you have a cough?",
            "shortness-of-breath": "Are you experiencing shortness of breath?",
            "contact-with-confirmed-case": "Have you had close contact with a confirmed case of COVID-19?"
        }

        # Create tkinter StringVars to hold the user's answers
        self.vars = {key: tk.StringVar(value="no") for key in self.questions.keys()}

        # Create the UI widgets
        self.create_widgets()

    def create_widgets(self):
        """Creates and arranges the labels and radio buttons for the UI."""
        for i, (key, question) in enumerate(self.questions.items()):
            label = tk.Label(self.root, text=question)
            label.grid(row=i, column=0, sticky="w", padx=10, pady=5)
            yes_button = tk.Radiobutton(self.root, text="Yes", variable=self.vars[key], value="yes")
            yes_button.grid(row=i, column=1, padx=5)
            no_button = tk.Radiobutton(self.root, text="No", variable=self.vars[key], value="no")
            no_button.grid(row=i, column=2, padx=5)

        diagnose_button = tk.Button(self.root, text="Diagnose", command=self.diagnose)
        diagnose_button.grid(row=len(self.questions), column=1, pady=20)

    def diagnose(self):
        """Runs the expert system diagnosis based on user input."""
        # Reset the CLIPS environment to clear previous facts
        self.env.reset()

        # Assert facts into the environment based on user's 'yes' answers
        for key, var in self.vars.items():
            if var.get() == "yes":
                if key == "contact-with-confirmed-case":
                    self.env.assert_string(f"({key} yes)")
                else:
                    # Assert the simplified symptom fact
                    self.env.assert_string(f"(symptom {key})")

        # Run the CLIPS inference engine
        self.env.run()

        # Find the result from the asserted facts
        result = "Low Risk"  # Default result
        for fact in self.env.facts():
            # The result fact has the structure (result "Risk Level")
            if str(fact).startswith("(result"):
                result = str(fact).split('"')[1]
                break

        # Display the final diagnosis in a message box
        messagebox.showinfo("Diagnosis Result", f"Your potential risk is: {result}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CovidExpertSystem(root)
    root.mainloop()
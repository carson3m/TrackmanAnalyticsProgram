import tkinter as tk
from tkinter import messagebox, ttk
from PythonFiles.pitch_analysis_app import PitchAnalysisApp
from PythonFiles.pitcher_summary import PitcherSummary


class PitcherSelectionUI:
    def __init__(self, loader):
        self.loader = loader

    def launch(self, root):
        self.app = PitchAnalysisApp(self.loader, root)

        self.pitcher_var = tk.StringVar(root)
        pitcher_names = sorted(self.loader.df['Pitcher'].dropna().unique())
        if pitcher_names:
            self.pitcher_var.set(pitcher_names[0])

        dropdown = tk.OptionMenu(root, self.pitcher_var, *pitcher_names)
        dropdown.pack(pady=10)

        single_button = tk.Button(root, text="Show Summary", command=self.show_pitcher_summary)
        single_button.pack(pady=5)

        all_button = tk.Button(root, text="Show All in Tabs", command=self.show_all_pitchers_in_tabs)
        all_button.pack(pady=5)

    def show_pitcher_summary(self):
        pitcher_name = self.pitcher_var.get()
        self.app.show_pitcher_summary(pitcher_name)

    def show_all_pitchers_in_tabs(self):
        for widget in self.app.parent.winfo_children():
            widget.destroy()

        notebook = ttk.Notebook(self.app.parent)
        notebook.pack(fill='both', expand=True)

        for pitcher_name in sorted(self.loader.df['Pitcher'].dropna().unique()):
            summary = PitcherSummary(self.loader.df, pitcher_name)
            frame = summary.get_summary_frame(notebook)
            notebook.add(frame, text=pitcher_name)


import tkinter as tk
from tkinter import ttk, messagebox
from PythonFiles.pitch_analysis_app import PitchAnalysisApp
from PythonFiles.pitcher_summary import PitcherSummary
from PythonFiles.batter_summary import BatterSummary

class PlayerSelectionUI:
    def __init__(self, loader):
        self.loader = loader
        self.df = loader.df

    def launch(self, root):
        self.app = PitchAnalysisApp(self.loader, root)

        # UI variables
        self.team_var = tk.StringVar(root)
        self.role_var = tk.StringVar(root)
        self.player_var = tk.StringVar(root)

        # Step 1: Select Team
        teams = sorted(set(self.df['PitcherTeam'].dropna().unique()).union(
                        set(self.df['BatterTeam'].dropna().unique())))
        if teams:
            self.team_var.set(teams[0])
        tk.Label(root, text="Select Team:").pack()
        tk.OptionMenu(root, self.team_var, *teams, command=self._update_players).pack(pady=2)

        # Step 2: Select Role
        tk.Label(root, text="Select Role:").pack()
        tk.OptionMenu(root, self.role_var, "Pitcher", "Hitter", command=self._update_players).pack(pady=2)
        self.role_var.set("Pitcher")

        # Step 3: Select Player
        tk.Label(root, text="Select Player:").pack()
        self.player_menu = tk.OptionMenu(root, self.player_var, "")
        self.player_menu.pack(pady=2)

        # Buttons
        tk.Button(root, text="Show Summary", command=self.show_summary).pack(pady=10)

        self._update_players()

    def _update_players(self, *_):
        team = self.team_var.get()
        role = self.role_var.get()

        if role == "Pitcher":
            players = self.df[self.df['PitcherTeam'] == team]['Pitcher'].dropna().unique()
        else:
            players = self.df[self.df['BatterTeam'] == team]['Batter'].dropna().unique()

        players = sorted(set(players))
        self.player_var.set(players[0] if players else "")

        # Rebuild dropdown
        self.player_menu['menu'].delete(0, 'end')
        for name in players:
            self.player_menu['menu'].add_command(label=name, command=tk._setit(self.player_var, name))

    def show_summary(self):
        player_name = self.player_var.get()
        role = self.role_var.get()

        if not player_name:
            messagebox.showerror("Error", "Please select a player.")
            return

        if role == "Pitcher":
            self.app.show_pitcher_summary(player_name)
        else:
            self.app.show_batter_summary(player_name)


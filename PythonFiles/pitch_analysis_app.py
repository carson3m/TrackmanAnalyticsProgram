
import tkinter as tk
from PythonFiles.strike_zone_plotter import StrikeZonePlotter
from PythonFiles.pitcher_summary import PitcherSummary
from PythonFiles.batter_summary import BatterSummary

class PitchAnalysisApp:
    def __init__(self, loader, parent):
        self.loader = loader
        self.parent = parent
        self.menu_frame = None
        self.summary_frame = tk.Frame(parent)
        self.summary_frame.pack(fill='both', expand=True)
        self.plotter = StrikeZonePlotter()

    def _show_menu(self):
        if self.summary_frame:
            self.summary_frame.pack_forget()
        if not self.menu_frame:
            from PythonFiles.player_selection_ui import PlayerSelectionUI
            self.menu_frame = tk.Frame(self.parent)
            self.menu_frame.pack(fill='x')
            ui = PlayerSelectionUI(self.loader)
            ui.launch(self.menu_frame)
        else:
            self.menu_frame.pack(fill='x')

    def show_pitcher_summary(self, pitcher_name):
        if self.menu_frame:
            self.menu_frame.pack_forget()
        self._clear_summary_frame()
        summary = PitcherSummary(self.loader.df, pitcher_name, self._show_menu)
        frame = summary.get_summary_frame(self.summary_frame)
        frame.pack(fill='both', expand=True)

    def show_batter_summary(self, batter_name):
        if self.menu_frame:
            self.menu_frame.pack_forget()
        self._clear_summary_frame()
        summary = BatterSummary(self.loader.df, batter_name, self._show_menu)
        frame = summary.get_summary_frame(self.summary_frame)
        frame.pack(fill='both', expand=True)

    def _clear_summary_frame(self):
        for widget in self.summary_frame.winfo_children():
            widget.destroy()

    # Optional analysis utilities
    def run_strike_zone_plot_all_pitches(self):
        all_pitches = self.loader.get_dataframe()
        strikes = all_pitches[all_pitches['PitchCall'] == 'StrikeCalled']
        balls = all_pitches[all_pitches['PitchCall'] == 'BallCalled']
        self.plotter.plot_pitch_calls(strikes, balls)
        self.plotter.add_strike_zone()
        self.plotter.finalize_plot('All Pitches Strike Zone Plot')
        self.plotter.show()

    def run_strike_zone_plot_for_pitcher(self, pitcher_name):
        pitcher_data = self.loader.df[self.loader.df['Pitcher'] == pitcher_name]
        self.plotter.plot_pitches_thrown(pitcher_data)
        self.plotter.add_strike_zone()
        self.plotter.finalize_plot(f'{pitcher_name} Pitch Locations')
        self.plotter.show()

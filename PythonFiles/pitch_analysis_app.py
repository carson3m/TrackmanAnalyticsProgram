import matplotlib.pyplot as plt
from PythonFiles.strike_zone_plotter import StrikeZonePlotter
import seaborn as sns
from PythonFiles.pitcher_summary import PitcherSummary


class PitchAnalysisApp:
    def __init__(self, loader, parent):
        self.loader = loader
        self.plotter = StrikeZonePlotter()
        self.parent = parent

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

        for index, row in pitcher_data.iterrows():
            print(f"Pitch Type: {row['AutoPitchType']} | Outcome: {row['PitchCall']} | Location: ({row['PlateLocSide']}, {row['PlateLocHeight']})")

        self.plotter.add_strike_zone()
        self.plotter.finalize_plot(f'{pitcher_name} Pitch Locations')
        self.plotter.show()

    def show_pitcher_summary(self, pitcher_name):
        # Clear existing summary frames
        for widget in self.parent.winfo_children():
            if isinstance(widget, type(self.parent)) or isinstance(widget, PitcherSummary):
                widget.destroy()
            elif isinstance(widget, type(widget)) and hasattr(widget, 'winfo_children'):
                for sub in widget.winfo_children():
                    sub.destroy()

        df = self.loader.get_dataframe()
        summary = PitcherSummary(df, pitcher_name)
        summary_frame = summary.get_summary_frame(self.parent)
        summary_frame.pack(fill='both', expand=True)

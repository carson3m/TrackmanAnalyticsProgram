
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.patches as patches

class BatterSummary:
    def __init__(self, df, batter_name, on_back):
        self.df_all = df[df['Batter'] == batter_name]
        self.name = batter_name
        self.on_back = on_back
        self.filtered_df = self.df_all.copy()
        self.pitch_type_col = 'AutoPitchType'

    def get_summary_frame(self, parent):
        self.frame = tk.Frame(parent)

        self._add_batting_metrics(self.frame)
        self._plot_pitch_type_bar(self.frame)
        self._plot_strike_zone(self.frame)

        tk.Button(parent, text='Back to Menu', command=self.on_back).pack(pady=10)

        return self.frame

    def _add_batting_metrics(self, parent):
        total_pitches = len(self.df_all)
        at_bats = self.df_all[['Inning', 'Top/Bottom', 'PAofInning']].drop_duplicates().shape[0]
        pitch_outcomes = self.df_all['PitchCall'].value_counts()

        summary = f"⚾ Batting Summary for {self.name}\n"
        summary += f"Total Pitches Faced: {total_pitches}\n"
        summary += f"Total At-Bats: {at_bats}\n"
        summary += "\nPitch Outcomes:\n"
        for outcome, count in pitch_outcomes.items():
            summary += f"- {outcome}: {count}\n"

        tk.Label(parent, text=summary, justify='left', anchor='w', font=('Courier', 10)).pack(fill='x', padx=5, pady=5)

    def _plot_pitch_type_bar(self, parent):
        if self.filtered_df.empty:
            return

        usage = self.filtered_df[self.pitch_type_col].value_counts()

        fig, ax = plt.subplots(figsize=(6, 4))
        usage.plot(kind='bar', ax=ax)
        ax.set_title('Pitch Types Faced')
        ax.set_xlabel('Pitch Type')
        ax.set_ylabel('Count')
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=5, pady=5)

        plt.close(fig)


    def _plot_strike_zone(self, parent):
        if not all(col in self.filtered_df.columns for col in ['PlateLocSide', 'PlateLocHeight', self.pitch_type_col]):
            return

        fig, ax = plt.subplots(figsize=(6, 7))
        grouped = self.filtered_df.groupby(self.pitch_type_col)

        for pitch_type, group in grouped:
            ax.scatter(group['PlateLocSide'], group['PlateLocHeight'], label=pitch_type, alpha=0.6, zorder=2)

        inch_to_feet = 1 / 12.0
        inner_width = 19.91 * inch_to_feet
        inner_bottom = 19.47 * inch_to_feet
        inner_top = 40.53 * inch_to_feet
        rect = patches.Rectangle(
            (-inner_width / 2, inner_bottom),
            inner_width,
            inner_top - inner_bottom,
            linewidth=2,
            edgecolor='black',
            linestyle='--',
            facecolor='none',
            zorder=3
        )
        ax.add_patch(rect)

        ax.set_xlim(-2, 2)
        ax.set_ylim(0, 5)
        ax.set_aspect('equal', adjustable='box')
        ax.set_title('Strike Zone (Pitches Faced)')
        ax.set_xlabel('Horizontal Location')
        ax.set_ylabel('Vertical Location')
        ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1))
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=5, pady=5)

        plt.close(fig)

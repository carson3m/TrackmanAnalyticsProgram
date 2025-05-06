import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd

class PitcherSummary:
    def __init__(self, df, pitcher_name, on_back):
        self.df_all = df[df['Pitcher'] == pitcher_name]
        self.name = pitcher_name
        self.on_back = on_back
        self.filtered_df = self.df_all.copy()
        self.pitch_type_col = 'AutoPitchType'
        self.checkbox_vars = {}

    def get_summary_frame(self, parent):
        self.frame = tk.Frame(parent)

        self._add_command_metrics(self.frame)
        self._add_avg_velocities(self.frame)
        self._add_pitch_type_filter_ui(self.frame)

        self.plot_container = tk.Frame(self.frame)
        self.plot_container.pack(fill='x', pady=10)

        self._update_plots()

        tk.Button(parent, text='Back to Menu', command=self.on_back).pack(pady=10)

        return self.frame

    def _add_command_metrics(self, parent):
        cols = ['PitchofPA', 'PitchCall', 'Inning', 'Top/Bottom', 'PAofInning']
        if not all(col in self.df_all.columns for col in cols):
            tk.Label(parent, text="Required columns missing for command metrics.").pack()
            return

        df = self.df_all.copy()
        df['AtBatID'] = df['Inning'].astype(str) + '_' + df['Top/Bottom'] + '_' + df['PAofInning'].astype(str)
        first_pitches = df[df['PitchofPA'] == 1]
        first_pitch_strikes = first_pitches[first_pitches['PitchCall'].isin(['StrikeCalled', 'InPlay'])]
        total_fp = len(first_pitches)
        strikes_fp = len(first_pitch_strikes)
        fp_strike_pct = (strikes_fp / total_fp * 100) if total_fp > 0 else 0

        strike_calls = df[df['PitchCall'].isin(['StrikeCalled', 'InPlay', 'FoulBall', 'SwingingStrike'])]
        strike_pct = (len(strike_calls) / len(df)) * 100 if len(df) > 0 else 0

        summary = f"🎯 Command Metrics for {self.name}\n"
        summary += f"Total Pitches: {len(df)}\n"
        summary += f"First-Pitch Strike %: {fp_strike_pct:.2f}%\n"
        summary += f"Overall Strike %: {strike_pct:.2f}%\n"

        tk.Label(parent, text=summary, justify='left', anchor='w', font=('Courier', 10)).pack(fill='x', padx=5, pady=5)

    def _add_avg_velocities(self, parent):
        if 'RelSpeed' not in self.df_all.columns:
            return

        avg_speeds = self.df_all.groupby(self.pitch_type_col)['RelSpeed'].mean().sort_values()
        summary = "Avg Velocities:\n" + "\n".join(f"- {pt}: {v:.1f} mph" for pt, v in avg_speeds.items())
        tk.Label(parent, text=summary, justify='left', anchor='w', font=('Courier', 10)).pack(fill='x', padx=5, pady=5)

    def _add_pitch_type_filter_ui(self, parent):
        filter_frame = tk.Frame(parent)
        tk.Label(filter_frame, text="Filter by Pitch Type:").pack(anchor='w')

        for pt in sorted(self.df_all[self.pitch_type_col].dropna().unique()):
            var = tk.BooleanVar(value=True)
            chk = tk.Checkbutton(filter_frame, text=pt, variable=var)
            chk.pack(anchor='w', side='left')
            self.checkbox_vars[pt] = var

        apply_btn = tk.Button(filter_frame, text="Apply Filters", command=self._apply_filters)
        apply_btn.pack(side='left', padx=10)
        filter_frame.pack(fill='x', pady=5)

    def _apply_filters(self):
        selected = [pt for pt, var in self.checkbox_vars.items() if var.get()]
        self.filtered_df = self.df_all[self.df_all[self.pitch_type_col].isin(selected)]

        for widget in self.plot_container.winfo_children():
            widget.destroy()

        self._update_plots()

    def _update_plots(self):
        pie_frame = tk.Frame(self.plot_container)
        pie_frame.pack(fill='x', pady=10)
        self._plot_pitch_type_pie(pie_frame)

        zone_frame = tk.Frame(self.plot_container)
        zone_frame.pack(fill='x', pady=10)
        self._plot_strike_zone(zone_frame)

    def _plot_pitch_type_pie(self, parent):
        if self.filtered_df.empty:
            return

        usage = self.filtered_df[self.pitch_type_col].value_counts()
        labels = [f"{pt}: {pct:.1f}%" for pt, pct in (usage / usage.sum() * 100).items()]

        fig, ax = plt.subplots(figsize=(6, 5))
        wedges, _ = ax.pie(usage, labels=None, startangle=90)
        ax.set_title('Pitch Type Usage')
        ax.legend(wedges, labels, loc='center left', bbox_to_anchor=(1.1, 0.5))
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill='both', expand=True, padx=5, pady=5)
        
        plt.close(fig)

    def _plot_strike_zone(self, parent):
        if not all(col in self.filtered_df.columns for col in ['PlateLocSide', 'PlateLocHeight', self.pitch_type_col]):
            return

        fig, ax = plt.subplots(figsize=(6, 7))
        grouped = self.filtered_df.groupby(self.pitch_type_col)

        for pitch_type, group in grouped:
            ax.scatter(group['PlateLocSide'], group['PlateLocHeight'], label=pitch_type, alpha=0.6, zorder=2)

        # Add strike zone rectangle
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
        ax.set_title('Strike Zone')
        ax.set_xlabel('Horizontal Location')
        ax.set_ylabel('Vertical Location')
        ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1))
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill='both', expand=True, padx=5, pady=5)
        
        plt.close(fig)

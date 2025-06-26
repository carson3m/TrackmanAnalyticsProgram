from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import seaborn as sns
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QScrollArea, QFrame
import pandas as pd


class LiveMetricsPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.main_layout = QVBoxLayout()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.inner_widget = QWidget()
        self.inner_layout = QVBoxLayout()
        self.inner_widget.setLayout(self.inner_layout)

        self.scroll_area.setWidget(self.inner_widget)
        self.main_layout.addWidget(self.scroll_area)
        self.setLayout(self.main_layout)

    def update_stats(self, df: pd.DataFrame):
        # Ensure required analysis columns exist


        # Clear previous metrics
        for i in reversed(range(self.inner_layout.count())):
            widget = self.inner_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        if df.empty or "AutoPitchType" not in df.columns:
            return
        
        for col in ["result", "swing", "contact", "hit_type", "discard"]:
            if col not in df.columns:
                df.loc[:, col] = None if col != "discard" else False
                
        if "discard" in df.columns:
            df = df[df["discard"] == False]
        # Remove discarded pitches
        grouped = df.groupby("AutoPitchType")

        for pitch_type, group in grouped:
            speed_avg = group["pitch_speed"].dropna().mean()
            spin_avg = group["spin_rate"].dropna().mean()

            total_pitches = len(group)
            # STRIKE %
            strikes = group['result'].isin([
                'Strike Called', 'Swing and Miss', 'Foul Ball', 'In Play - Out', 'In Play - Hit'
            ]).sum()
            strike_pct = (strikes / len(group)) * 100 if len(group) > 0 else 0

            # SWINGS
            swing_df = group[group['swing'].isin(['Full Swing', 'Check Swing', 'Bunt'])]
            swing_count = len(swing_df)
            swing_pct = (swing_count / total_pitches) * 100 if total_pitches else 0

            # WHIFF RATE
            whiffs = swing_df[swing_df['result'] == 'Swing and Miss']
            whiff_rate = (len(whiffs) / swing_count) * 100 if swing_count else 0

            # CONTACT %
            contacts = swing_df[swing_df['contact'].isin(['Weak', 'Medium', 'Hard'])]
            contact_pct = (len(contacts) / swing_count) * 100 if swing_count else 0

            # HARD HIT %
            hard_hits = contacts[contacts['contact'] == 'Hard']
            hard_hit_pct = (len(hard_hits) / len(contacts)) * 100 if len(contacts) else 0

            label = QLabel(
                f"<b>{pitch_type}</b><br>"
                f"Avg Speed: {speed_avg:.1f} mph<br>"
                f"Avg Spin: {spin_avg:.0f} rpm<br>"
                f"Strike %: {strike_pct:.1f}%<br>"
                f"Swing %: {swing_pct:.1f}%<br>"
                f"Whiff Rate: {whiff_rate:.1f}%<br>"
                f"Contact %: {contact_pct:.1f}%<br>"
                f"Hard Hit %: {hard_hit_pct:.1f}%"
            )
            label.setFrameStyle(QFrame.Box)
            label.setContentsMargins(5, 5, 5, 5)
            self.inner_layout.addWidget(label)

        # Existing plots
        self.add_plot("Pitch Usage", self.plot_usage, df)
        self.add_plot("Spin Rate by Type", self.plot_spin_rate, df)
        self.add_plot("Velocity by Type", self.plot_velocity, df)
        self.add_plot("Release Point by Type", self.plot_release_point, df)
        self.add_plot("Pitch Break (Horz vs Induced Vert)", self.plot_pitch_break, df)

    def add_plot(self, title: str, plotting_func, df, *args):
        fig = Figure(figsize=(5, 3))
        canvas = FigureCanvas(fig)
        canvas.setMinimumHeight(250)
        ax = fig.add_subplot(111)
        plotting_func(df, ax, *args)
        ax.set_title(title)
        fig.tight_layout()
        self.inner_layout.addWidget(canvas)

    @staticmethod
    def plot_release_point(df, ax):
        if 'release_side' in df.columns and 'release_height' in df.columns:
            grouped = df.groupby("AutoPitchType")
            for name, group in grouped:
                ax.scatter(group["release_side"], group["release_height"], alpha=0.5, label=name)
            ax.set_xlabel("Release Side (ft)")
            ax.set_ylabel("Release Height (ft)")
            ax.set_xlim(5, -5)
            ax.set_ylim(1, 7)
            ax.legend()

    @staticmethod
    def plot_spin_rate(df, ax):
        if "spin_rate" in df.columns and "AutoPitchType" in df.columns:
            df = df.dropna(subset=["spin_rate"])
            sns.boxplot(data=df, x="AutoPitchType", y="spin_rate", ax=ax)
            ax.set_xlabel("Pitch Type")
            ax.set_ylabel("Spin Rate (rpm)")
            ax.tick_params(axis='x', rotation=45)

    @staticmethod
    def plot_velocity(df, ax):
        if "pitch_speed" in df.columns and "AutoPitchType" in df.columns:
            df = df.dropna(subset=["pitch_speed"])
            sns.boxplot(data=df, x="AutoPitchType", y="pitch_speed", ax=ax)
            ax.set_xlabel("Pitch Type")
            ax.set_ylabel("Velocity (mph)")
            ax.tick_params(axis='x', rotation=45)

    @staticmethod
    def plot_usage(df, ax):
        if "AutoPitchType" in df.columns:
            counts = df["AutoPitchType"].value_counts()
            counts.plot(kind="bar", ax=ax, color="skyblue")
            ax.set_xlabel("Pitch Type")
            ax.set_ylabel("Count")
            
    @staticmethod
    def plot_pitch_break(df, ax):
        if "movement_horizontal" not in df.columns or "induced_vertical" not in df.columns:
            ax.set_title("Break data unavailable")
            return

        grouped = df.groupby("AutoPitchType")
        for name, group in grouped:
            ax.scatter(group["movement_horizontal"], group["induced_vertical"], alpha=0.5, label=name)

        ax.axhline(0, color='gray', linestyle='--')
        ax.axvline(0, color='gray', linestyle='--')
        ax.set_xlabel("Horizontal Break (inches)")
        ax.set_ylabel("Induced Vertical Break (inches)")
        ax.legend()
        ax.set_xlim(-25, 25)
        ax.set_ylim(-25, 25)
        ax.set_aspect('equal', adjustable='box')


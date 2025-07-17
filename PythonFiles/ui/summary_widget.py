from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QSizePolicy, QPushButton, QScrollArea,
    QGroupBox, QLabel, QCheckBox, QSlider, QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import pandas as pd

from PythonFiles.summary.visuals import plot_pitch_type_pie
from PythonFiles.core.player_metrics import PlayerMetricsAnalyzer
from PythonFiles.ui.strike_zone_plotter import StrikeZonePlotter
from PythonFiles.summary.export import export_summary_to_pdf
from PythonFiles.core.statistics import calculate_whiff_rate, calculate_strike_rate, calculate_zone_rate


def get_pitch_type_column(df):
    if 'AutoPitchType' in df.columns:
        return 'AutoPitchType'
    elif 'TaggedPitchType' in df.columns:
        return 'TaggedPitchType'
    elif 'PitchCall' in df.columns:
        return 'PitchCall'
    else:
        return None

def create_slider(min_val, max_val, default_min, default_max):
    min_slider = QSlider()
    max_slider = QSlider()
    min_slider.setOrientation(Qt.Horizontal)
    max_slider.setOrientation(Qt.Horizontal)
    min_slider.setRange(min_val, max_val)
    max_slider.setRange(min_val, max_val)
    min_slider.setValue(default_min)
    max_slider.setValue(default_max)
    return min_slider, max_slider

class SummaryWidget(QWidget):
    def __init__(self, title, player_df, role, back_callback, player_name, live=False):
        super().__init__()
        self.live = live
        self.player_name = player_name
        self.df_all = player_df.copy()
        self.filtered_df = self.df_all.copy()
        self.plotter = StrikeZonePlotter()

        self.full_layout = QVBoxLayout()
        self.plot_container = QVBoxLayout()
        plot_container_widget = QWidget()
        plot_container_widget.setLayout(self.plot_container)
        plot_container_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.full_layout.addWidget(plot_container_widget)

        #self.summary_text = QTextEdit()
        #self.summary_text.setReadOnly(True)
        #self.summary_text.setMinimumHeight(300)
        #self.summary_text.setMaximumHeight(1000)
        #self.summary_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.metrics_table = QTableWidget()
        self.metrics_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.metrics_table.setMinimumHeight(200)

        self.full_layout.addWidget(self.metrics_table)
        #self.full_layout.addWidget(self.summary_text)

        if role == "Pitcher":
            self.add_filters()
        
        # Pitch Break Plot
        self.breaks_figure = Figure(figsize=(4, 4))
        self.breaks_canvas = FigureCanvas(self.breaks_figure)
        self.breaks_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plot_container.addWidget(self.breaks_canvas)

        # Release Point Plot
        self.release_figure = Figure(figsize=(6, 6))
        self.release_canvas = FigureCanvas(self.release_figure)
        self.release_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plot_container.addWidget(self.release_canvas)

        back_btn = QPushButton("Back to Menu")
        back_btn.clicked.connect(back_callback)
        self.full_layout.addWidget(back_btn)

        export_btn = QPushButton("Export to PDF")
        export_btn.clicked.connect(self.handle_export)
        self.full_layout.addWidget(export_btn)

        content_widget = QWidget()
        content_widget.setLayout(self.full_layout)
        content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_widget.setMinimumSize(self.full_layout.sizeHint())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(content_widget)

        outer_layout = QVBoxLayout(self)
        outer_layout.addWidget(scroll)

        self.render_summary()

    def add_filters(self):
        group = QGroupBox("Filters")
        layout = QVBoxLayout()

        pitch_col = get_pitch_type_column(self.df_all)
        self.pitch_type_checkboxes = []

        if pitch_col and pitch_col in self.df_all.columns:
            for pitch in sorted(self.df_all[pitch_col].dropna().unique()):
                cb = QCheckBox(pitch)
                cb.setChecked(True)
                layout.addWidget(cb)
                self.pitch_type_checkboxes.append(cb)
        else:
            layout.addWidget(QLabel("⚠️ No pitch type data available"))

        if 'Inning' in self.df_all.columns and not self.df_all['Inning'].isna().all():
            min_inning = int(self.df_all['Inning'].min())
            max_inning = int(self.df_all['Inning'].max())
            self.inning_min_slider, self.inning_max_slider = create_slider(min_inning, max_inning, min_inning, max_inning)
            self.inning_label = QLabel()
            self.update_inning_label()
            self.inning_min_slider.valueChanged.connect(self.update_inning_label)
            self.inning_max_slider.valueChanged.connect(self.update_inning_label)
            layout.addWidget(self.inning_label)
            layout.addWidget(self.inning_min_slider)
            layout.addWidget(self.inning_max_slider)
        else:
            layout.addWidget(QLabel("⚠️ No inning data available"))

        velocity_col = None
        if 'RelSpeed' in self.df_all.columns and not self.df_all['RelSpeed'].isna().all():
            velocity_col = 'RelSpeed'
        elif 'PitchSpeed' in self.df_all.columns and not self.df_all['PitchSpeed'].isna().all():
            velocity_col = 'PitchSpeed'

        if velocity_col:
            min_vel = int(self.df_all[velocity_col].min())
            max_vel = int(self.df_all[velocity_col].max())
            self.velocity_min_slider, self.velocity_max_slider = create_slider(min_vel, max_vel, min_vel, max_vel)
            self.velocity_label = QLabel()
            self.update_velocity_label()
            self.velocity_min_slider.valueChanged.connect(self.update_velocity_label)
            self.velocity_max_slider.valueChanged.connect(self.update_velocity_label)
            layout.addWidget(self.velocity_label)
            layout.addWidget(self.velocity_min_slider)
            layout.addWidget(self.velocity_max_slider)
        else:
            layout.addWidget(QLabel("⚠️ No velocity data available"))

        refresh_btn = QPushButton("Refresh Summary")
        refresh_btn.clicked.connect(self.refresh_summary)
        layout.addWidget(refresh_btn)

        group.setLayout(layout)
        self.full_layout.addWidget(group)
        
    def update_data(self, new_df):
        self.df_all = new_df.copy()
        self.filtered_df = self.df_all.copy()
        self.refresh_summary()


    def update_inning_label(self):
        self.inning_label.setText(
            f"Inning Range: {self.inning_min_slider.value()} – {self.inning_max_slider.value()}"
        )

    def update_velocity_label(self):
        self.velocity_label.setText(
            f"Velocity Range: {self.velocity_min_slider.value()} – {self.velocity_max_slider.value()}"
        )

    def refresh_summary(self):
        pitch_col = get_pitch_type_column(self.df_all)
        types = [cb.text() for cb in self.pitch_type_checkboxes if cb.isChecked()] if pitch_col else []
        filters = pd.Series([True] * len(self.df_all))

        if pitch_col:
            filters &= self.df_all[pitch_col].isin(types)
        if hasattr(self, 'inning_min_slider') and 'Inning' in self.df_all.columns:
            filters &= self.df_all['Inning'].between(self.inning_min_slider.value(), self.inning_max_slider.value())
        if hasattr(self, 'velocity_min_slider') and ('RelSpeed' in self.df_all.columns or 'PitchSpeed' in self.df_all.columns):
            vel_col = 'RelSpeed' if 'RelSpeed' in self.df_all.columns else 'PitchSpeed'
            filters &= self.df_all[vel_col].between(self.velocity_min_slider.value(), self.velocity_max_slider.value())

        self.filtered_df = self.df_all[filters]
        self.render_summary()

    def populate_metrics_table(self, df):
        self.metrics_table.clear()
        if df.empty:
            self.metrics_table.setRowCount(0)
            self.metrics_table.setColumnCount(0)
            return

        self.metrics_table.setColumnCount(len(df.columns))
        self.metrics_table.setRowCount(len(df))
        self.metrics_table.setHorizontalHeaderLabels(df.columns)

        for row in range(len(df)):
            for col in range(len(df.columns)):
                item = QTableWidgetItem(str(df.iat[row, col]))
                item.setFlags(Qt.ItemIsEnabled)
                self.metrics_table.setItem(row, col, item)
        self.metrics_table.resizeColumnsToContents()

    def render_summary(self):
        summary_lines = []

        # Mark zone location
        self.filtered_df["IsInZone"] = self.filtered_df.apply(
            lambda row: -0.83 <= row.get("PlateLocSide", 999) <= 0.83 and
                        1.5 <= row.get("PlateLocHeight", -999) <= 3.5,
            axis=1
        )

        num_pitches = len(self.filtered_df)
        if num_pitches == 0:
            #self.summary_text.setText("No pitches match the selected filters.")
            self.metrics_table.clear()
            return

        # Core efficiency stats
        whiff = calculate_whiff_rate(self.filtered_df)
        strike = calculate_strike_rate(self.filtered_df)
        zone = calculate_zone_rate(self.filtered_df)

        summary_lines.append(f"Total Pitches: {num_pitches}")
        summary_lines.append(f"Whiff Rate: {whiff:.1f}%")
        summary_lines.append(f"Strike Rate: {SummaryWidget.safe_percent(strike)}")
        summary_lines.append(f"Zone Rate: {zone:.1f}%")

        # Per-pitch-type metrics
        analyzer = PlayerMetricsAnalyzer(self.filtered_df, self.player_name)
        pitch_df = analyzer.per_pitch_type_metrics_df()
        self.populate_metrics_table(pitch_df)
        
        self.plot_pitch_breaks(self.filtered_df)
        self.plot_release_points(self.filtered_df)


    # Strike zone plot
        #self.add_plot(lambda ax: SummaryWidget.plot_summary_strike_zone(self.filtered_df, ax))
        #self.summary_text.setText("\n".join(summary_lines))

    def add_plot(self, plot_func):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        plot_func(ax)
        self.plot_canvas.draw()
        
    @staticmethod
    def safe_percent(val):
        return "N/A" if pd.isna(val) or val > 1000 else f"{val:.1f}%"

    def handle_export(self):
        try:
            summary_lines = []

            whiff = calculate_whiff_rate(self.filtered_df)
            strike = calculate_strike_rate(self.filtered_df)
            zone = calculate_zone_rate(self.filtered_df)
            total_pitches = len(self.filtered_df)

            #summary_lines.append(f"Total Pitches: {total_pitches}")
            #summary_lines.append(f"Whiff Rate: {whiff:.1f}%")
            #summary_lines.append(f"Strike Rate: {SummaryWidget.safe_percent(strike)}")
            #summary_lines.append(f"Zone Rate: {zone:.1f}%")

            #summary_text = "\n".join(summary_lines)

            def plot_breaks(ax):
                pitch_col = get_pitch_type_column(self.filtered_df)
                for pitch_type, group in self.filtered_df.groupby(pitch_col):
                    ax.scatter(group['HorzBreak'], group['InducedVertBreak'], label=pitch_type, alpha=0.7)
                ax.set_title("Pitch Breaks")
                ax.set_xlabel("Horizontal Break (in)")
                ax.set_ylabel("Vertical Break (in)")
                ax.axhline(0, color='gray', linestyle='--', linewidth=0.5)
                ax.axvline(0, color='gray', linestyle='--', linewidth=0.5)
                ax.set_aspect('auto')
                ax.set_xlim(-25, 25)
                ax.set_ylim(-25, 25)
                ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

            def plot_release(ax):
                pitch_col = get_pitch_type_column(self.filtered_df)
                for pitch_type, group in self.filtered_df.groupby(pitch_col):
                    ax.scatter(group['RelSide'], group['RelHeight'], label=pitch_type, alpha=0.7)
                ax.set_title("Release Points")
                ax.set_xlabel("Horizontal Release Side (ft)")
                ax.set_ylabel("Vertical Release Height (ft)")
                ax.axhline(0, color='gray', linestyle='--', linewidth=0.5)
                ax.axvline(0, color='gray', linestyle='--', linewidth=0.5)
                ax.set_aspect('auto')
                ax.set_xlim(-4, 4)
                ax.set_ylim(1, 6.5)
                ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

            pitch_df = PlayerMetricsAnalyzer(self.filtered_df, self.player_name).per_pitch_type_metrics_df()
            pdf_path = export_summary_to_pdf(
                self.player_name,
                summary_text="",
                plot_funcs=[plot_breaks, plot_release],
                metrics_df=pitch_df
            )

            QMessageBox.information(self, "Export Complete", f"PDF saved to: {pdf_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))

     
    @staticmethod
    def plot_summary_strike_zone(df, ax, title="Strike Zone – All Pitches"):
        strikes = df[df['IsInZone']]
        balls = df[~df['IsInZone']]

        ax.scatter(balls['PlateLocSide'], balls['PlateLocHeight'],
                    color='red', label='Outside Zone', alpha=0.5)
        ax.scatter(strikes['PlateLocSide'], strikes['PlateLocHeight'],
                    color='green', label='In Zone', alpha=0.5)

        ax.set_xlabel("Horizontal Location (ft)")
        ax.set_ylabel("Vertical Location (ft)")
        ax.set_title(title)

        # Draw strike zone rectangle
        ax.add_patch(
            plt.Rectangle((-0.83, 1.5), 1.66, 2.0,
                        linewidth=1, edgecolor='white', facecolor='none')
        )
        ax.legend()
        ax.set_xlim(-2.5, 2.5)
        ax.set_ylim(0, 5)
        
    def plot_pitch_breaks(self, df):
        self.breaks_figure.clear()
        ax = self.breaks_figure.add_subplot(111)
        pitch_col = get_pitch_type_column(df)

        for pitch_type, group in df.groupby(pitch_col):
            ax.scatter(
                group['HorzBreak'], group['InducedVertBreak'],
                label=pitch_type, alpha=0.7
            )

        ax.set_title("Pitch Breaks")
        ax.set_xlabel("Horizontal Break (in)")
        ax.set_ylabel("Vertical Break (in)")
        ax.axhline(0, color='gray', linestyle='--', linewidth=0.5)
        ax.axvline(0, color='gray', linestyle='--', linewidth=0.5)
        ax.set_aspect('equal', adjustable='box')
        ax.set_xlim(-25, 25)
        ax.set_ylim(-25, 25)
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))  # Move legend outside
        self.breaks_canvas.draw()

    def plot_release_points(self, df):
        self.release_figure.clear()
        ax = self.release_figure.add_subplot(111)
        pitch_col = get_pitch_type_column(df)

        for pitch_type, group in df.groupby(pitch_col):
            ax.scatter(
                group['RelSide'], group['RelHeight'],
                label=pitch_type, alpha=0.7
            )

        ax.set_title("Release Points")
        ax.set_xlabel("Horizontal Release Side (ft)")
        ax.set_ylabel("Vertical Release Height (ft)")
        ax.axhline(0, color='gray', linestyle='--', linewidth=0.5)
        ax.axvline(0, color='gray', linestyle='--', linewidth=0.5)
        ax.set_aspect('equal', adjustable='box')
            # ✅ Set fixed limits
        ax.set_xlim(-3.5, 3.5)
        ax.set_ylim(0, 6.5)
        ax.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
        self.release_canvas.draw()


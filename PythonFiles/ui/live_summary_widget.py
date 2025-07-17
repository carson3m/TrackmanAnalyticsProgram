from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea
from PythonFiles.ui.live_metrics_panel import LiveMetricsPanel
from PythonFiles.ui.live_pitch_table import LivePitchTable
from PythonFiles.ui.live_strike_zone_plot import LiveStrikeZonePlot

class LiveSummaryWidget(QWidget):
    def __init__(self, context_manager):
        super().__init__()
        self.context_manager = context_manager

        # Main layout becomes horizontal
        main_layout = QHBoxLayout()

        # LEFT SIDE: Live pitch visuals
        left_column = QVBoxLayout()
        self.metrics_panel = LiveMetricsPanel()
        self.zone_plot = LiveStrikeZonePlot()
        self.pitch_table = LivePitchTable(self.context_manager)

        left_column.addWidget(self.zone_plot)
        left_column.addWidget(self.pitch_table)

        # Wrap left column in QWidget
        left_widget = QWidget()
        left_widget.setLayout(left_column)
        main_layout.addWidget(left_widget, stretch=2)

        # RIGHT SIDE: Stat graphs (scrollable)
        graph_scroll = QScrollArea()
        graph_scroll.setWidgetResizable(True)
        graph_scroll.setFixedWidth(400)  # Adjust as needed
        graph_scroll.setWidget(self.metrics_panel)

        main_layout.addWidget(graph_scroll, stretch=1)

        self.setLayout(main_layout)

    def update(self, df):
        if df.empty:
            return

        pitcher = self.context_manager.pitcher_name

        # ✅ Always check new data for matching pitcher
        latest_df = df[df["pitcher"] == pitcher]
        if not latest_df.empty:
            latest = latest_df.iloc[-1]
            play_id = latest.get("play_id")
            if play_id and play_id not in self.pitch_table.seen_play_ids:
                self.pitch_table.update_rows(latest)

        # 🔄 Refresh clean view after update
        clean_df = self.pitch_table.get_clean_pitch_data()

        # ✅ Just in case — ensure 'pitcher' exists
        if "pitcher" not in clean_df.columns:
            clean_df["pitcher"] = pitcher

        filtered = clean_df[clean_df["pitcher"] == pitcher]

        self.metrics_panel.update_stats(filtered)
        self.zone_plot.update_plot(filtered)

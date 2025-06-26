from PyQt5.QtWidgets import (
    QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QComboBox, QCheckBox
)
from PyQt5.QtCore import Qt
import pandas as pd

class LivePitchTable(QWidget):
    def __init__(self, context_manager):
        super().__init__()
        self.context_manager = context_manager
        self.columns = [
            "Time", "Speed", "Spin", "Pitch Type",
            "Result", "Swing", "Contact", "Hit Type", "Discard?"
        ]
        self.table = QTableWidget(0, len(self.columns))  # ✅ This was missing
        self.table.setHorizontalHeaderLabels(self.columns)
        self.pitch_data = []
        self.seen_play_ids = set()

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)


    def update_rows(self, new_pitch: dict):
        if isinstance(new_pitch, pd.Series):
            new_pitch = new_pitch.to_dict()

        # ✅ Skip duplicate pitches by PlayId
        play_id = new_pitch.get("play_id")
        if play_id in self.seen_play_ids:
            return
        self.seen_play_ids.add(play_id)
        new_pitch["pitcher"] = self.context_manager.pitcher_name


        # Insert at the top
        self.pitch_data.insert(0, new_pitch)
        self.table.insertRow(0)

        self.table.setItem(0, 0, QTableWidgetItem(str(new_pitch.get("timestamp", "-"))))
        self.table.setItem(0, 1, QTableWidgetItem(f"{new_pitch.get("pitch_speed", 0):.1f}"))
        self.table.setItem(0, 2, QTableWidgetItem(f"{new_pitch.get("spin_rate", 0):.0f}"))
        self.table.setItem(0, 3, QTableWidgetItem(new_pitch.get("pitch_type", "-")))

        # Add dropdowns
        self.add_dropdown(0, 4, [
            "Strike Called", "Ball Called", "Swing and Miss",
            "Foul Ball", "In Play - Out", "In Play - Hit", "Hit By Pitch"
        ], new_pitch, "result")

        self.add_dropdown(0, 5, [
            "No Swing", "Full Swing", "Check Swing", "Bunt"
        ], new_pitch, "swing")

        self.add_dropdown(0, 6, [
            "None", "Weak", "Medium", "Hard"
        ], new_pitch, "contact")

        self.add_dropdown(0, 7, [
            "None", "Single", "Double", "Triple", "Home Run",
            "Lineout", "Flyout", "Groundout", "Popup"
        ], new_pitch, "hit_type")

        self.add_discard_checkbox(0, 8, new_pitch)


    def add_dropdown(self, row, column, options, pitch_dict, key):
        combo = QComboBox()
        combo.addItems(options)
        combo.setCurrentText(options[0])
        pitch_dict[key] = options[0]

        combo.currentTextChanged.connect(lambda value: self.on_dropdown_changed(pitch_dict, key, value))
        self.table.setCellWidget(row, column, combo)

    def add_discard_checkbox(self, row, column, pitch_dict):
        checkbox = QCheckBox()
        checkbox.stateChanged.connect(lambda state, pd=pitch_dict: pd.update({"discard": state == Qt.Checked}))
        self.table.setCellWidget(row, column, checkbox)

    def get_clean_pitch_data(self) -> pd.DataFrame:
        return pd.DataFrame([p for p in self.pitch_data if not p.get("discard", False)])
    
    def on_dropdown_changed(self, pitch_dict, key, value):
        pitch_dict[key] = value

        # 🔁 Trigger live metrics refresh
        parent = self.parent()
        if parent and hasattr(parent, "metrics_panel") and hasattr(self, "get_clean_pitch_data"):
            parent.metrics_panel.update_stats(self.get_clean_pitch_data())

# ui/pitcher_context_panel.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QLineEdit, QRadioButton, QButtonGroup
)
from PythonFiles.core.context_manager import LiveContextManager

class PitcherContextPanel(QWidget):
    def __init__(self, context_manager: LiveContextManager):
        super().__init__()
        self.context_manager = context_manager

        layout = QVBoxLayout()

        # Pitcher Controls
        pitcher_layout = QHBoxLayout()
        self.pitcher_combo = QComboBox()
        self.pitcher_input = QLineEdit()
        add_pitcher_btn = QPushButton("Add Pitcher")
        add_pitcher_btn.clicked.connect(self.add_pitcher)
        self.pitcher_combo.currentTextChanged.connect(self.context_manager.set_pitcher)

        pitcher_layout.addWidget(QLabel("Pitcher:"))
        pitcher_layout.addWidget(self.pitcher_combo)
        pitcher_layout.addWidget(self.pitcher_input)
        pitcher_layout.addWidget(add_pitcher_btn)

        # Team Controls
        team_layout = QHBoxLayout()
        self.team_combo = QComboBox()
        self.team_input = QLineEdit()
        add_team_btn = QPushButton("Add Team")
        add_team_btn.clicked.connect(self.add_team)
        self.team_combo.currentTextChanged.connect(self.context_manager.set_team)

        team_layout.addWidget(QLabel("Team:"))
        team_layout.addWidget(self.team_combo)
        team_layout.addWidget(self.team_input)
        team_layout.addWidget(add_team_btn)

        # Live / Warm-Up Toggle
        toggle_layout = QHBoxLayout()
        toggle_layout.addWidget(QLabel("Pitch Type:"))
        self.live_radio = QRadioButton("Live")
        self.warmup_radio = QRadioButton("Warm-Up")
        self.live_radio.setChecked(True)

        self.pitch_type_group = QButtonGroup()
        self.pitch_type_group.addButton(self.live_radio)
        self.pitch_type_group.addButton(self.warmup_radio)

        self.live_radio.toggled.connect(lambda checked: self.context_manager.set_category("Live") if checked else None)
        self.warmup_radio.toggled.connect(lambda checked: self.context_manager.set_category("Warm-Up") if checked else None)

        toggle_layout.addWidget(self.live_radio)
        toggle_layout.addWidget(self.warmup_radio)

        # Final Assembly
        layout.addLayout(pitcher_layout)
        layout.addLayout(team_layout)
        layout.addLayout(toggle_layout)
        self.setLayout(layout)

    def add_pitcher(self):
        name = self.pitcher_input.text().strip()
        if name and name not in [self.pitcher_combo.itemText(i) for i in range(self.pitcher_combo.count())]:
            self.pitcher_combo.addItem(name)
            self.pitcher_combo.setCurrentText(name)
            self.context_manager.set_pitcher(name)
        self.pitcher_input.clear()

    def add_team(self):
        name = self.team_input.text().strip()
        if name and name not in [self.team_combo.itemText(i) for i in range(self.team_combo.count())]:
            self.team_combo.addItem(name)
            self.team_combo.setCurrentText(name)
            self.context_manager.set_team(name)
        self.team_input.clear()


import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QFileDialog, QStackedWidget, QMessageBox, QScrollArea, QGroupBox,
    QCheckBox, QSlider, QTextEdit, QSizePolicy
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from summary.text import command_metrics_string, avg_velocity_string, batting_summary_string
from summary.visuals import plot_pitch_type_pie, plot_pitch_type_bar, plot_strike_zone
from summary.statistics import calculate_whiff_rate, calculate_strike_rate, calculate_zone_rate
from summary.export import export_summary_to_pdf

class PlayerSelectionWidget(QWidget):
    def __init__(self, df, show_summary_callback):
        super().__init__()
        self.df = df
        self.show_summary_callback = show_summary_callback

        layout = QVBoxLayout()
        self.team_dropdown = QComboBox()
        self.role_dropdown = QComboBox()
        self.role_dropdown.addItems(["Pitcher", "Hitter"])
        self.player_dropdown = QComboBox()
        self.show_button = QPushButton("Show Summary")

        self.team_dropdown.currentTextChanged.connect(self.update_players)
        self.role_dropdown.currentTextChanged.connect(self.update_players)
        self.show_button.clicked.connect(self.handle_show_summary)

        layout.addWidget(QLabel("Select Team:"))
        layout.addWidget(self.team_dropdown)
        layout.addWidget(QLabel("Select Role:"))
        layout.addWidget(self.role_dropdown)
        layout.addWidget(QLabel("Select Player:"))
        layout.addWidget(self.player_dropdown)
        layout.addWidget(self.show_button)
        self.setLayout(layout)

        self.populate_teams()

    def populate_teams(self):
        teams = sorted(set(self.df['PitcherTeam'].dropna()).union(set(self.df['BatterTeam'].dropna())))
        self.team_dropdown.addItems(teams)
        self.update_players()

    def update_players(self):
        team = self.team_dropdown.currentText()
        role = self.role_dropdown.currentText()
        if role == "Pitcher":
            players = self.df[self.df['PitcherTeam'] == team]['Pitcher'].dropna().unique()
        else:
            players = self.df[self.df['BatterTeam'] == team]['Batter'].dropna().unique()
        self.player_dropdown.clear()
        self.player_dropdown.addItems(sorted(players))

    def handle_show_summary(self):
        player = self.player_dropdown.currentText()
        role = self.role_dropdown.currentText()
        if not player:
            QMessageBox.warning(self, "Error", "Please select a player.")
            return
        self.show_summary_callback(role, player)

class SummaryWidget(QWidget):
    def __init__(self, title, player_df, role, back_callback, player_name):
        super().__init__()
        self.player_name = player_name
        self.df_all = player_df.copy()
        self.filtered_df = self.df_all.copy()

        self.full_layout = QVBoxLayout()
        self.plot_container = QVBoxLayout()

        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMinimumHeight(120)
        self.summary_text.setMaximumHeight(150)
        self.summary_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.full_layout.addWidget(self.summary_text)

        if role == "Pitcher":
            self.add_filters()

        self.full_layout.addLayout(self.plot_container)

        back_btn = QPushButton("Back to Menu")
        back_btn.clicked.connect(back_callback)
        self.full_layout.addWidget(back_btn)

        export_btn = QPushButton("Export to PDF")
        export_btn.clicked.connect(self.handle_export)
        self.full_layout.addWidget(export_btn)

        content_widget = QWidget()
        content_widget.setLayout(self.full_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(content_widget)

        outer_layout = QVBoxLayout(self)
        outer_layout.addWidget(scroll)

        self.render_summary()

    def add_filters(self):
        group = QGroupBox("Filters")
        layout = QVBoxLayout()

        self.pitch_type_checkboxes = []
        for pitch in sorted(self.df_all['AutoPitchType'].dropna().unique()):
            cb = QCheckBox(pitch)
            cb.setChecked(True)
            layout.addWidget(cb)
            self.pitch_type_checkboxes.append(cb)

        self.inning_min_slider = QSlider(Qt.Horizontal)
        self.inning_max_slider = QSlider(Qt.Horizontal)
        min_in = int(self.df_all['Inning'].min())
        max_in = int(self.df_all['Inning'].max())
        self.inning_min_slider.setRange(min_in, max_in)
        self.inning_max_slider.setRange(min_in, max_in)
        self.inning_min_slider.setValue(min_in)
        self.inning_max_slider.setValue(max_in)
        self.inning_label = QLabel()
        self.update_inning_label()

        self.inning_min_slider.valueChanged.connect(self.update_inning_label)
        self.inning_max_slider.valueChanged.connect(self.update_inning_label)

        layout.addWidget(self.inning_label)
        layout.addWidget(self.inning_min_slider)
        layout.addWidget(self.inning_max_slider)

        self.velocity_min_slider = QSlider(Qt.Horizontal)
        self.velocity_max_slider = QSlider(Qt.Horizontal)
        min_vel = int(self.df_all['RelSpeed'].min())
        max_vel = int(self.df_all['RelSpeed'].max())
        self.velocity_min_slider.setRange(min_vel, max_vel)
        self.velocity_max_slider.setRange(min_vel, max_vel)
        self.velocity_min_slider.setValue(min_vel)
        self.velocity_max_slider.setValue(max_vel)
        self.velocity_label = QLabel()
        self.update_velocity_label()

        self.velocity_min_slider.valueChanged.connect(self.update_velocity_label)
        self.velocity_max_slider.valueChanged.connect(self.update_velocity_label)

        layout.addWidget(self.velocity_label)
        layout.addWidget(self.velocity_min_slider)
        layout.addWidget(self.velocity_max_slider)

        refresh_btn = QPushButton("Refresh Summary")
        refresh_btn.clicked.connect(self.refresh_summary)
        layout.addWidget(refresh_btn)

        group.setLayout(layout)
        self.full_layout.addWidget(group)

    def update_inning_label(self):
        self.inning_label.setText(f"Inning Range: {self.inning_min_slider.value()} – {self.inning_max_slider.value()}")

    def update_velocity_label(self):
        self.velocity_label.setText(f"Velocity Range: {self.velocity_min_slider.value()} – {self.velocity_max_slider.value()}")

    def refresh_summary(self):
        types = [cb.text() for cb in self.pitch_type_checkboxes if cb.isChecked()]
        in_min, in_max = self.inning_min_slider.value(), self.inning_max_slider.value()
        v_min, v_max = self.velocity_min_slider.value(), self.velocity_max_slider.value()
        self.filtered_df = self.df_all[
            (self.df_all['AutoPitchType'].isin(types)) &
            (self.df_all['Inning'].between(in_min, in_max)) &
            (self.df_all['RelSpeed'].between(v_min, v_max))
        ]
        self.render_summary()

    def render_summary(self):
        df = self.filtered_df
        self.summary_text.setPlainText(
            command_metrics_string(df, self.player_name) +
            avg_velocity_string(df) +
            f"\nWhiff Rate: {calculate_whiff_rate(df):.2f}%\n" +
            f"Strike Rate: {calculate_strike_rate(df):.2f}%\n" +
            f"Zone Rate: {calculate_zone_rate(df):.2f}%\n"
        )
        while self.plot_container.count():
            child = self.plot_container.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        fig1, ax1 = plt.subplots(figsize=(6, 4))
        plot_pitch_type_pie(df, ax1)
        canvas1 = FigureCanvas(fig1)
        canvas1.setMinimumSize(600, 400)
        canvas1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.plot_container.addWidget(canvas1)

        fig2, ax2 = plt.subplots(figsize=(6, 6))
        plot_strike_zone(df, ax2)
        canvas2 = FigureCanvas(fig2)
        canvas2.setMinimumSize(600, 600)
        canvas2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.plot_container.addWidget(canvas2)

    def handle_export(self):
        df = self.filtered_df.copy()
        summary = self.summary_text.toPlainText()
        plot_funcs = [
            lambda ax: plot_pitch_type_pie(df, ax),
            lambda ax: plot_strike_zone(df, ax)
        ]
        filepath = export_summary_to_pdf(self.player_name, summary, plot_funcs)
        QMessageBox.information(self, "Export Complete", f"PDF saved to:{filepath}")

class MainWindow(QMainWindow):
    def __init__(self, df):
        super().__init__()
        self.setWindowTitle("Trackman Analytics")
        self.setGeometry(100, 100, 1000, 800)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.df = df
        self.selection_widget = PlayerSelectionWidget(df, self.show_summary)
        self.stack.addWidget(self.selection_widget)

    def show_summary(self, role, name):
        df = self.df[self.df['Pitcher'] == name] if role == "Pitcher" else self.df[self.df['Batter'] == name]
        widget = SummaryWidget(f"Summary for {name}", df, role, self.show_menu, name)
        self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)

    def show_menu(self):
        self.stack.setCurrentWidget(self.selection_widget)

def main():
    app = QApplication(sys.argv)
    file_dialog = QFileDialog()
    default_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
    file_path, _ = file_dialog.getOpenFileName(None, "Select CSV", default_dir, "CSV Files (*.csv)")
    if not file_path:
        print("No file selected. Exiting.")
        return
    df = pd.read_csv(file_path)
    window = MainWindow(df)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

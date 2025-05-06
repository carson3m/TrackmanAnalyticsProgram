import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QFileDialog, QStackedWidget, QMessageBox, QScrollArea, QGroupBox
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from summary.text import (
    command_metrics_string, avg_velocity_string,
    batting_summary_string
)
from summary.visuals import (
    plot_pitch_type_pie, plot_pitch_type_bar, plot_strike_zone
)
from summary.statistics import (
    calculate_whiff_rate, calculate_strike_rate, calculate_zone_rate
)
from summary.export import export_summary_to_pdf

class PlayerSelectionWidget(QWidget):
    def __init__(self, df, show_summary_callback):
        super().__init__()
        self.df = df
        self.show_summary_callback = show_summary_callback

        self.layout = QVBoxLayout()

        self.team_label = QLabel("Select Team:")
        self.team_dropdown = QComboBox()
        self.role_label = QLabel("Select Role:")
        self.role_dropdown = QComboBox()
        self.role_dropdown.addItems(["Pitcher", "Hitter"])
        self.player_label = QLabel("Select Player:")
        self.player_dropdown = QComboBox()

        self.show_button = QPushButton("Show Summary")
        self.show_button.clicked.connect(self.handle_show_summary)

        self.team_dropdown.currentTextChanged.connect(self.update_players)
        self.role_dropdown.currentTextChanged.connect(self.update_players)

        self.layout.addWidget(self.team_label)
        self.layout.addWidget(self.team_dropdown)
        self.layout.addWidget(self.role_label)
        self.layout.addWidget(self.role_dropdown)
        self.layout.addWidget(self.player_label)
        self.layout.addWidget(self.player_dropdown)
        self.layout.addWidget(self.show_button)
        self.setLayout(self.layout)

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
    def __init__(self, title, summary_text, plot_funcs, back_callback, player_name):
        super().__init__()

        outer_layout = QVBoxLayout(self)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content_widget = QWidget()
        layout = QVBoxLayout()
        content_widget.setLayout(layout)
        content_widget.setMinimumHeight(1000)

        # Navigation buttons
        back_button = QPushButton("Back to Menu")
        export_button = QPushButton("Export to PDF")
        button_layout = QVBoxLayout()
        button_layout.addWidget(back_button)
        button_layout.addWidget(export_button)

        back_button.clicked.connect(back_callback)
        export_button.clicked.connect(lambda: self.handle_export(summary_text, plot_funcs, player_name))

        layout.addLayout(button_layout)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; font-size: 18px")
        layout.addWidget(title_label)

        summary_box = QGroupBox("Summary")
        summary_layout = QVBoxLayout()
        summary_label = QLabel(summary_text)
        summary_label.setStyleSheet("font-family: Courier; white-space: pre")
        summary_layout.addWidget(summary_label)
        summary_box.setLayout(summary_layout)
        layout.addWidget(summary_box)

        for func in plot_funcs:
            if func.__name__ == "<lambda>":
                fig, ax = plt.subplots(figsize=(6, 6)) if "plot_strike_zone" in func.__code__.co_names else plt.subplots()
            else:
                fig, ax = plt.subplots()
            func(ax)
            canvas = FigureCanvas(fig)

            plot_box = QGroupBox()
            plot_layout = QVBoxLayout()
            plot_layout.addWidget(canvas)
            plot_box.setLayout(plot_layout)
            layout.addWidget(plot_box)

        scroll_area.setWidget(content_widget)
        outer_layout.addWidget(scroll_area)

    def handle_export(self, summary_text, plot_funcs, player_name):
        filepath = export_summary_to_pdf(player_name, summary_text, plot_funcs)
        QMessageBox.information(self, "Export Complete", f"PDF saved to:\n{filepath}")

class MainWindow(QMainWindow):
    def __init__(self, df):
        super().__init__()
        self.setWindowTitle("Trackman Analytics")
        self.setGeometry(100, 100, 900, 800)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.selection_widget = PlayerSelectionWidget(df, self.show_summary)
        self.stack.addWidget(self.selection_widget)

        self.df = df

    def show_summary(self, role, player_name):
        if role == "Pitcher":
            player_df = self.df[self.df['Pitcher'] == player_name]
            summary_text = command_metrics_string(player_df, player_name) + avg_velocity_string(player_df)
            summary_text += f"\nWhiff Rate: {calculate_whiff_rate(player_df):.2f}%"
            summary_text += f"\nStrike Rate: {calculate_strike_rate(player_df):.2f}%"
            summary_text += f"\nZone Rate: {calculate_zone_rate(player_df):.2f}%\n"
            plot_funcs = [
                lambda ax: plot_pitch_type_pie(player_df, ax),
                lambda ax: plot_strike_zone(player_df, ax)
            ]
        else:
            player_df = self.df[self.df['Batter'] == player_name]
            summary_text = batting_summary_string(player_df, player_name)
            plot_funcs = [
                lambda ax: plot_pitch_type_bar(player_df, ax),
                lambda ax: plot_strike_zone(player_df, ax)
            ]

        summary_widget = SummaryWidget(f"Summary for {player_name}", summary_text, plot_funcs, self.show_menu, player_name)
        self.stack.addWidget(summary_widget)
        self.stack.setCurrentWidget(summary_widget)

    def show_menu(self):
        self.stack.setCurrentWidget(self.selection_widget)

def main():
    app = QApplication(sys.argv)

    file_dialog = QFileDialog()
    default_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
    file_path, _ = file_dialog.getOpenFileName(
        None, "Select CSV Data File", default_dir, "CSV Files (*.csv)"
    )

    if not file_path:
        print("No file selected. Exiting.")
        return

    df = pd.read_csv(file_path)
    window = MainWindow(df)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

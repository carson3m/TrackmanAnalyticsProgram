
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit,
    QMessageBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
from ui.strike_zone_plotter import StrikeZonePlotter
from core.network.udp_listener import TrackmanUDPListener
import json

def classify_pitch(location):
    if not location:
        return None
    x = location.get("Side")
    y = location.get("Height")
    if x is None or y is None:
        return None

    # Standard MLB strike zone bounds
    if -0.83 <= x <= 0.83 and 1.5 <= y <= 3.5:
        return "StrikeCalled"
    else:
        return "BallCalled"

class PlayerSelectionWidget(QWidget):
    def __init__(self, df, show_summary_callback, live=False):
        super().__init__()
        self.current_summary_widget = None
        self.df = df
        self.df_all = self.df.copy()
        self.show_summary_callback = show_summary_callback
        self.recording_enabled = True
        self.live=live

        layout = QVBoxLayout()
        self.setLayout(layout)
        
        #if self.live:
            #self.trackman_listener = TrackmanUDPListener(callback=self.handle_trackman_data)
            #self.trackman_listener.start()

        self.plotter = StrikeZonePlotter()
        self.figure = Figure(figsize=(5, 5))
        self.plot_canvas = FigureCanvas(self.figure)
        layout.addWidget(self.plot_canvas)

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

        if self.live:
            self.active_pitcher_dropdown = QComboBox()
            self.pitcher_input = QLineEdit()
            self.team_input = QLineEdit()
            self.add_pitcher_button = QPushButton("Add Pitcher")
            self.pitcher_to_team = {}

            self.add_pitcher_button.clicked.connect(self.add_pitcher)

            layout.addWidget(QLabel("Active Pitcher:"))
            layout.addWidget(self.active_pitcher_dropdown)
            layout.addWidget(QLabel("Pitcher:"))
            layout.addWidget(self.pitcher_input)
            layout.addWidget(QLabel("Team:"))
            layout.addWidget(self.team_input)
            layout.addWidget(self.add_pitcher_button)

            self.toggle_recording_btn = QPushButton("Pause Recording")
            self.toggle_recording_btn.setCheckable(True)
            self.toggle_recording_btn.clicked.connect(self.toggle_recording)
            layout.addWidget(self.toggle_recording_btn)
            
        self.populate_teams()

    def handle_trackman_data(self, message):
        print("\n[Trackman] 🔍 Raw message received:")
        print(json.dumps(message, indent=2))
        if not self.recording_enabled:
            print("[Trackman] ⏹ Pitch ignored (recording paused)")
            return

        try:
            pitch = message.get("Pitch")
            hit = message.get("Hit")
        
            pitcher_name = self.active_pitcher_dropdown.currentText().strip()
            if not pitcher_name:
                print("[Trackman] ⚠️ No active pitcher selected — skipping play.")
                return
            
            team_name = self.pitcher_to_team.get(pitcher_name, "Unknown")

            location = pitch.get("Location", {}) if pitch else {}
            pitch_call = classify_pitch(location)
            # Calculate IsInZone (used by summary_widget.py)
            zone_x = location.get("Side")
            zone_y = location.get("Height")
            is_in_zone = (
                zone_x is not None and zone_y is not None and
                -0.83 <= zone_x <= 0.83 and 1.5 <= zone_y <= 3.5
            )


            row = {
            "Time": message.get("Time"),
            "TrackId": message.get("PlayId"),
            "PitchCall": pitch_call if pitch_call else "Unknown",
            "PitchSpeed": pitch.get("Speed") if pitch else None,
            "SpinRate": pitch.get("SpinRate") if pitch else None,
            "PlateLocSide": location.get("Side"),
            "PlateLocHeight": location.get("Height"),
            "IsInZone": is_in_zone,
            "ExitVelo": hit.get("Speed") if hit else None,
            "LaunchAngle": hit.get("Angle") if hit else None,
            "CarryDistance": hit.get("Distance") if hit else None,
            "Pitcher": pitcher_name,
            "PitcherTeam": team_name,
            }

            if any(pd.notna(v) for v in row.values()):
                self.df_all = pd.concat([self.df_all, pd.DataFrame([row])], ignore_index=True)
                self.df = self.df_all.copy()
                print(f"[Trackman] Ingested play: {row['TrackId']}")
                print(f"[Visual] Plotting {row['PitchCall']}")
                self.refresh_visuals()

                if hasattr(self.parent(), "current_summary_widget") and self.parent().current_summary_widget:
                    self.parent().current_summary_widget.update_data(self.df)
            else: 
                print("[Trackman] ⚠️ Skipped empty row (no useful data)")
        except Exception as e:
            print(f"[Trackman] Data handling error: {e}")

    def refresh_visuals(self):
        if hasattr(self, 'plot_canvas'):
            self.figure.clf()
            ax = self.figure.add_subplot(111)

            if self.live:
                if "IsInZone" not in self.df_all.columns:
                    # Recompute in case it's missing
                    self.df_all["IsInZone"] = self.df_all.apply(
                        lambda row: -0.83 <= row.get("PlateLocSide", 0) <= 0.83 and 1.5 <= row.get("PlateLocHeight", 0) <= 3.5,
                        axis=1
                    )
                strikes = self.df_all[self.df_all["IsInZone"] == True]
                balls = self.df_all[self.df_all["IsInZone"] == False]
            else:
                strikes = self.df_all[self.df_all['PitchCall'] == 'Strike']
                balls = self.df_all[self.df_all['PitchCall'] == 'Ball']

            print(f"[Visual] Plotting {len(strikes)} strikes and {len(balls)} balls")
            self.plotter.plot_pitch_calls(strikes, balls, ax)
            self.plot_canvas.draw()

    def update_data(self, new_df):
        self.df = new_df
        self.populate_teams()

    def add_pitcher(self):
        name = self.pitcher_input.text().strip()
        team = self.team_input.text().strip()

        if name:
            if name not in [self.active_pitcher_dropdown.itemText(i) for i in range(self.active_pitcher_dropdown.count())]:
                self.active_pitcher_dropdown.addItem(name)
                self.player_dropdown.addItem(name)
            self.active_pitcher_dropdown.setCurrentText(name)

            self.pitcher_to_team[name] = team

            if team and team not in [self.team_dropdown.itemText(i) for i in range(self.team_dropdown.count())]:
                self.team_dropdown.addItem(team)

            self.pitcher_input.clear()
            self.team_input.clear()
            
            # Auto-select the first added pitcher in live mode
            if self.live and self.active_pitcher_dropdown.count() == 1:
                self.active_pitcher_dropdown.setCurrentIndex(0)


    def populate_teams(self):
        if 'PitcherTeam' not in self.df.columns or 'BatterTeam' not in self.df.columns:
            self.team_dropdown.clear()
            self.player_dropdown.clear()
            return
        teams = sorted(set(self.df['PitcherTeam'].dropna()).union(set(self.df['BatterTeam'].dropna())))
        self.team_dropdown.clear()
        self.team_dropdown.addItems(teams)
        self.update_players()

    def update_players(self):
        team = self.team_dropdown.currentText()
        role = self.role_dropdown.currentText()
        col = 'Pitcher' if role == "Pitcher" else 'Batter'
        team_col = 'PitcherTeam' if role == "Pitcher" else 'BatterTeam'

        print(f"🔍 Filtering players for team='{team}', role='{role}', using column='{col}'")

        if team_col not in self.df.columns or col not in self.df.columns:
            print(f"⚠️ Missing columns: {team_col} or {col}")
            return

        filtered_df = self.df[self.df[team_col] == team]
        print(f"✅ Found {len(filtered_df)} rows for team {team}")

        players = filtered_df[col].dropna().unique()
        print(f"🎯 Unique players: {players}")

        self.player_dropdown.clear()
        self.player_dropdown.addItems(sorted(players))

    def handle_show_summary(self):
        player = self.player_dropdown.currentText()
        role = self.role_dropdown.currentText()
        if not player:
            QMessageBox.warning(self, "Error", "Please select a player.")
            return
        self.show_summary_callback(role, player)

    def toggle_recording(self):
        self.recording_enabled = not self.recording_enabled
        if self.recording_enabled:
            self.toggle_recording_btn.setText("Pause Recording")
            print("[Trackman] 🟢 Recording resumed")
        else:
            self.toggle_recording_btn.setText("Resume Recording")
            print("[Trackman] ⏸️ Recording paused")

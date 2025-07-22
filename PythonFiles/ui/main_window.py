
from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QPushButton, QVBoxLayout, QWidget
from datetime import datetime
from PythonFiles.ui.player_selection_widget import PlayerSelectionWidget
from PythonFiles.ui.summary_widget import SummaryWidget
from PythonFiles.ui.umpire_accuracy_widget import UmpireAccuracyWidget
from PythonFiles.ui.live_summary_widget import LiveSummaryWidget
from PythonFiles.core.session_manager import SessionManager
from PythonFiles.ui.pitcher_context_panel import PitcherContextPanel
from PythonFiles.core.classifier.pitch_classifier import classify_pitch

from PyQt5.QtCore import QTimer
import pandas as pd

class MainWindow(QMainWindow):
    def __init__(self, df, live=False):
        super().__init__()
        self.setWindowTitle("MoundVision Analytics")
        self.resize(1200, 900)
        self.df = df
        self.live = live

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        if self.live:
            self.session = SessionManager()
            self.session.start_live_mode()

            self.context_manager = self.session.get_context_manager()
            self.live_buffer = self.session.get_buffer()

            self.pitcher_panel = PitcherContextPanel(self.context_manager)
            self.summary_widget = LiveSummaryWidget(self.context_manager)

            layout = QVBoxLayout()
            layout.addWidget(self.pitcher_panel)
            layout.addWidget(self.summary_widget)

            container = QWidget()
            container.setLayout(layout)
            self.stack.addWidget(container)
            self.stack.setCurrentWidget(container)

            self.timer = QTimer()
            self.timer.setInterval(200)
            self.timer.timeout.connect(self.update_summary)
            self.timer.start()

    
        else:
            # CSV mode setup
            self.selection_widget = PlayerSelectionWidget(self.df, self.show_summary, live=self.live)
            self.stack.addWidget(self.selection_widget)

            umpire_btn = QPushButton("Umpire Accuracy")
            umpire_btn.clicked.connect(self.show_umpire_accuracy)
            self.selection_widget.layout().addWidget(umpire_btn)

    def show_summary(self, role, name):
        df_source = self.selection_widget.df_all  # always use updated data
        name = name.strip()

        # Debugging: Show what values exist
        print(f"🔍 Looking for {role}: '{name}'")
        col = "Pitcher" if role == "Pitcher" else "Batter"
        if col not in df_source.columns:
            print(f"⚠️ Cannot show summary — '{col}' column missing.")
            return

        df_source[col] = df_source[col].astype(str).str.strip()  # normalize names
        df = df_source[df_source[col] == name]

        if df.empty:
            print(f"⚠️ Cannot show summary — no matching rows for '{name}' in column '{col}'")
            return

        widget = SummaryWidget(f"Summary for {name}", df, role, self.show_menu, name, live=self.live)
        self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)
        self.current_summary_widget = widget

    def show_menu(self):
        self.stack.setCurrentWidget(self.selection_widget)

    def show_umpire_accuracy(self):
        widget = UmpireAccuracyWidget(self.df, self.show_menu)
        self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)

    def closeEvent(self, event):
        try:
            if hasattr(self, 'session'):
                self.session.stop()
            if hasattr(self, 'selection_widget') and hasattr(self.selection_widget, 'trackman_listener'):
                self.selection_widget.trackman_listener.stop()
        except Exception as e:
            print(f"[Trackman] Shutdown error: {e}")
        super().closeEvent(event)
        
    def update_summary(self):
        df = self.live_buffer.to_dataframe()
        self.summary_widget.update(df)


'''
    def on_new_pitch(self, pitch_json):
        from core.pitch_parser import parse_pitch_message

        if pitch_json.get("Kind") != "Pitch":
            return
        if self.context_manager.pitch_category != "Live":
            return  # Ignore warm-up pitches

        print("[Debug] Full JSON received:")
        import json
        print(json.dumps(pitch_json, indent=2))  # pretty print

        parsed = parse_pitch_message(pitch_json, self.context_manager)
        if not parsed:
            print("[Trackman] ⚠️ Parsing failed or incomplete pitch data.")
            return

        try:
            parsed.update(self.context_manager.get_context())
            parsed["timestamp"] = datetime.fromisoformat(
                pitch_json["Time"].replace("Z", "+00:00")
            ).strftime("%H:%M:%S")
            
            parsed.setdefault("pitch_type", "Unknown")


            classified_type = classify_pitch(parsed)
            parsed["AutoPitchType"] = classified_type
            
            parsed["pitcher"] = self.context_manager.pitcher_name

            self.live_buffer.add_pitch(parsed)
            print(f"[Live] ✅ {parsed['pitcher']} | {parsed['AutoPitchType']} | {parsed['pitch_speed']} mph")

        except Exception as e:
            print(f"[Trackman] General error during processing: {e}")
'''


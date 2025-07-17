# core/session_manager.py

from datetime import datetime
from PythonFiles.core.classifier.pitch_classifier import classify_pitch
from PythonFiles.core.pitch_parser import parse_pitch_message
from PythonFiles.core.network.udp_listener import TrackmanUDPListener
from PythonFiles.core.data_buffer import LiveDataBuffer
from PythonFiles.core.context_manager import LiveContextManager

class SessionManager:
    def __init__(self):
        self.context_manager = LiveContextManager()
        self.live_buffer = LiveDataBuffer()
        self.udp_listener = None

    def start_live_mode(self):
        self.udp_listener = TrackmanUDPListener(callback=self.on_new_pitch)
        self.udp_listener.start()

    def stop(self):
        if self.udp_listener:
            self.udp_listener.stop()

    def get_context_manager(self):
        return self.context_manager

    def get_buffer(self):
        return self.live_buffer

    def on_new_pitch(self, pitch_json):
        if pitch_json.get("Kind") != "Pitch":
            return
        if self.context_manager.pitch_category != "Live":
            return

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
            parsed["AutoPitchType"] = classify_pitch(parsed)
            parsed["pitcher"] = self.context_manager.pitcher_name

            self.live_buffer.add_pitch(parsed)
            print(f"[Live] ✅ {parsed['pitcher']} | {parsed['AutoPitchType']} | {parsed['pitch_speed']} mph")

        except Exception as e:
            print(f"[Trackman] Error during pitch handling: {e}")

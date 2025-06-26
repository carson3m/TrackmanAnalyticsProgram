# core/live_data_buffer.py
from collections import deque
import pandas as pd

class LiveDataBuffer:
    def __init__(self, max_size=500):
        self.buffer = deque(maxlen=max_size)
        self.last_pitch_key = None  # NEW

    def _make_key(self, pitch):
        return (
            pitch.get("timestamp"),
            round(pitch.get("pitch_speed", 0), 1),
            pitch.get("AutoPitchType")
        )

    def add_pitch(self, parsed_dict):
        key = self._make_key(parsed_dict)
        if key == self.last_pitch_key:
            return  # Duplicate, ignore
        self.buffer.append(parsed_dict)
        self.last_pitch_key = key  # Track most recent

    def to_dataframe(self):
        return pd.DataFrame(self.buffer)

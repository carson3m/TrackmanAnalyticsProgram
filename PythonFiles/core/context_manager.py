# core/live_context_manager.py

class LiveContextManager:
    def __init__(self):
        self.pitcher_name = "Unknown"
        self.team = "Unknown"
        self.pitch_category = "Live"  # or "Warm-Up"

    def set_pitcher(self, name):
        self.pitcher_name = name

    def set_team(self, team):
        self.team = team

    def set_category(self, category):
        if category in ["Live", "Warm-Up"]:
            self.pitch_category = category

    def get_context(self):
        return {
            "pitcher": self.pitcher_name,
            "team": self.team,
            "pitch_category": self.pitch_category,
        }

    def reset(self):
        self.pitcher_name = "Unknown"
        self.team = "Unknown"
        self.pitch_category = "Live"

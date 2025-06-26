import pandas as pd
class ModeManager:
    def __init__(self, live_mode=True):
        self.live_mode = live_mode

    def is_live(self):
        return self.live_mode

    def get_initial_df(self):
        return pd.DataFrame()

    def setup_data_flow(self, widget):
        pass

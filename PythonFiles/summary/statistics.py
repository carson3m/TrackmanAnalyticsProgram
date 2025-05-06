import numpy as np

def calculate_whiff_rate(df):
    swings = df[df['PitchCall'].isin(['FoulBall', 'InPlay', 'SwingingStrike'])]
    whiffs = df[df['PitchCall'] == 'SwingingStrike']
    if len(swings) == 0:
        return 0.0
    return len(whiffs) / len(swings) * 100

def calculate_strike_rate(df):
    strikes = df[df['PitchCall'].isin(['StrikeCalled', 'SwingingStrike', 'FoulBall', 'InPlay'])]
    if len(df) == 0:
        return 0.0
    return len(strikes) / len(df) * 100

def calculate_zone_rate(df):
    if 'PlateLocSide' not in df or 'PlateLocHeight' not in df:
        return 0.0
    zone_df = df[(df['PlateLocSide'].between(-0.83, 0.83)) & (df['PlateLocHeight'].between(1.62, 3.38))]
    if len(df) == 0:
        return 0.0
    return len(zone_df) / len(df) * 100
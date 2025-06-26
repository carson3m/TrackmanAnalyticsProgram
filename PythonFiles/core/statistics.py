import pandas as pd

def calculate_whiff_rate(df: pd.DataFrame) -> float:
    """Whiff Rate = Swinging strikes / (all swings)."""
    if 'PitchCall' not in df.columns:
        return 0.0
    swings = df[df['PitchCall'].isin(['FoulBall', 'InPlay', 'SwingingStrike'])]
    whiffs = df[df['PitchCall'] == 'SwingingStrike']
    return len(whiffs) / len(swings) * 100 if len(swings) > 0 else 0.0

def calculate_strike_rate(df: pd.DataFrame) -> float:
    """Strike Rate = All strikes / total pitches."""
    if 'PitchCall' not in df.columns or len(df) == 0:
        return 0.0
    strikes = df[df['PitchCall'].isin(['StrikeCalled', 'SwingingStrike', 'FoulBall', 'InPlay'])]
    return len(strikes) / len(df) * 100

def calculate_zone_rate(df: pd.DataFrame) -> float:
    """Zone Rate = Pitches inside strike zone / total pitches."""
    if 'IsInZone' not in df.columns or len(df) == 0:
        return 0.0
    return df['IsInZone'].sum() / len(df) * 100

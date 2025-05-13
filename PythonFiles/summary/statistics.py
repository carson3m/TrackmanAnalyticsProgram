
import numpy as np
import pandas as pd

def calculate_whiff_rate(df: pd.DataFrame) -> float:
    """Calculate whiff rate: Swinging strikes / all swings."""
    swings = df[df['PitchCall'].isin(['FoulBall', 'InPlay', 'SwingingStrike'])]
    whiffs = df[df['PitchCall'] == 'SwingingStrike']
    if len(swings) == 0:
        return 0.0
    return len(whiffs) / len(swings) * 100

def calculate_strike_rate(df: pd.DataFrame) -> float:
    """Calculate strike rate: All strikes / total pitches."""
    if 'PitchCall' not in df.columns:
        return 0.0
    strikes = df[df['PitchCall'].isin(['StrikeCalled', 'SwingingStrike', 'FoulBall', 'InPlay'])]
    return len(strikes) / len(df) * 100 if len(df) > 0 else 0.0

def calculate_zone_rate(df: pd.DataFrame) -> float:
    """Calculate zone rate: Pitches in strike zone / total pitches."""
    if 'Zone' not in df.columns:
        return 0.0
    return df['Zone'].notna().sum() / len(df) * 100 if len(df) > 0 else 0.0

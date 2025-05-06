def command_metrics_string(df, name):
    cols = ['PitchofPA', 'PitchCall', 'Inning', 'Top/Bottom', 'PAofInning']
    if not all(col in df.columns for col in cols):
        return "Required columns missing for command metrics."

    df = df.copy()
    df['AtBatID'] = df['Inning'].astype(str) + '_' + df['Top/Bottom'] + '_' + df['PAofInning'].astype(str)
    first_pitches = df[df['PitchofPA'] == 1]
    first_pitch_strikes = first_pitches[first_pitches['PitchCall'].isin(['StrikeCalled', 'InPlay'])]
    total_fp = len(first_pitches)
    strikes_fp = len(first_pitch_strikes)
    fp_strike_pct = (strikes_fp / total_fp * 100) if total_fp > 0 else 0

    strike_calls = df[df['PitchCall'].isin(['StrikeCalled', 'InPlay', 'FoulBall', 'SwingingStrike'])]
    strike_pct = (len(strike_calls) / len(df)) * 100 if len(df) > 0 else 0

    summary = f"\n🎯 Command Metrics for {name}\n"
    summary += f"Total Pitches: {len(df)}\n"
    summary += f"First-Pitch Strike %: {fp_strike_pct:.2f}%\n"
    summary += f"Overall Strike %: {strike_pct:.2f}%\n"
    return summary

def avg_velocity_string(df, pitch_type_col='AutoPitchType'):
    if 'RelSpeed' not in df.columns:
        return ""
    avg_speeds = df.groupby(pitch_type_col)['RelSpeed'].mean().sort_values()
    summary = "\nAvg Velocities:\n" + "\n".join(f"- {pt}: {v:.1f} mph" for pt, v in avg_speeds.items())
    return summary

def batting_summary_string(df, name):
    total_pitches = len(df)
    at_bats = df[['Inning', 'Top/Bottom', 'PAofInning']].drop_duplicates().shape[0]
    pitch_outcomes = df['PitchCall'].value_counts()

    summary = f"\n⚾ Batting Summary for {name}\n"
    summary += f"Total Pitches Faced: {total_pitches}\n"
    summary += f"Total At-Bats: {at_bats}\n\nPitch Outcomes:\n"
    for outcome, count in pitch_outcomes.items():
        summary += f"- {outcome}: {count}\n"
    return summary

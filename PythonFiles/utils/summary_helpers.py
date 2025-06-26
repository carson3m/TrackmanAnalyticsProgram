
import matplotlib.pyplot as plt

def get_pitch_type_column(df):
    return 'AutoPitchType' if 'AutoPitchType' in df.columns else 'TaggedPitchType'

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
    if pitch_type_col not in df.columns:
        return "Pitch type column missing."

    avg_speeds = df.groupby(pitch_type_col)['RelSpeed'].mean().sort_values()
    summary = "\nAvg Velocities:\n" + "\n".join(f"- {pt}: {v:.1f} mph" for pt, v in avg_speeds.items())
    return summary

def plot_pitch_type_pie(df, ax, pitch_col='AutoPitchType', pitch_colors=None):
    usage = df[pitch_col].value_counts()
    labels = usage.index.tolist()
    values = usage.values.tolist()

    # Use consistent colors
    if pitch_colors is None:
        pitch_colors = {
            'Four-Seam': 'red',
            'Sinker': 'blue',
            'Curveball': 'green',
            'Slider': 'purple',
            'Changeup': 'orange',
            'Knuckleball': 'cyan',
            'Splitter': 'yellow'
        }
    colors = [pitch_colors.get(p, 'gray') for p in labels]

    wedges, _ = ax.pie(values, labels=None, colors=colors, startangle=90)
    ax.set_title("Pitch Type Usage")
    ax.legend(wedges, labels, loc='center left', bbox_to_anchor=(1, 0.5))


def plot_pitch_type_bar(df, ax, pitch_type_col='AutoPitchType'):
    if pitch_type_col not in df.columns:
        ax.set_title("No pitch type column")
        return
    counts = df[pitch_type_col].value_counts()
    ax.bar(counts.index, counts.values)
    ax.set_xticklabels(counts.index, rotation=45)
    ax.set_title("Pitch Type Count")
    ax.set_ylabel("Count")
    
def is_pitch_in_strike_zone(x, z):
    """Return True if pitch is in zone based on x/z location."""
    return x is not None and z is not None and -0.83 <= x <= 0.83 and 1.5 <= z <= 3.5

    

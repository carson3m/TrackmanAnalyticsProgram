import matplotlib.pyplot as plt
import matplotlib.patches as patches


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


def plot_pitch_type_pie(df, ax, pitch_type_col='AutoPitchType'):
    usage = df[pitch_type_col].value_counts()
    labels = [f"{pt}: {pct:.1f}%" for pt, pct in (usage / usage.sum() * 100).items()]
    wedges, _ = ax.pie(usage, labels=None, startangle=90)
    ax.set_title("Pitch Type Usage")
    ax.legend(wedges, labels, loc='center left', bbox_to_anchor=(1.1, 0.5))


def plot_pitch_type_bar(df, ax, pitch_type_col='AutoPitchType'):
    usage = df[pitch_type_col].value_counts()
    usage.plot(kind='bar', ax=ax)
    ax.set_title("Pitch Types Faced")
    ax.set_xlabel("Pitch Type")
    ax.set_ylabel("Count")


def plot_strike_zone(df, ax, pitch_type_col='AutoPitchType'):
    if not all(col in df.columns for col in ['PlateLocSide', 'PlateLocHeight']):
        return

    grouped = df.groupby(pitch_type_col)
    for pitch_type, group in grouped:
        ax.scatter(group['PlateLocSide'], group['PlateLocHeight'], label=pitch_type, alpha=0.6, zorder=2)

    # Add strike zone rectangle
    inch_to_feet = 1 / 12.0
    inner_width = 19.91 * inch_to_feet
    inner_bottom = 19.47 * inch_to_feet
    inner_top = 40.53 * inch_to_feet
    rect = patches.Rectangle(
        (-inner_width / 2, inner_bottom),
        inner_width,
        inner_top - inner_bottom,
        linewidth=2.5,
        edgecolor='black',
        linestyle='--',
        facecolor='none',
        zorder=3
    )
    ax.add_patch(rect)

    ax.set_xlim(-2, 2)
    ax.set_ylim(0, 5)
    ax.set_aspect('equal', adjustable='datalim')
    ax.set_box_aspect(1)
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.set_title('Strike Zone', fontsize=12)
    ax.set_xlabel('Horizontal Location')
    ax.set_ylabel('Vertical Location')
    ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1))


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

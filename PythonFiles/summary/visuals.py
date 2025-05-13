
# Deprecated: plotting logic is now handled by strike_zone_plotter_cleaned.py
# File retained for backward compatibility or legacy reference.

def plot_pitch_type_pie(df, ax, pitch_type_col='AutoPitchType'):
    usage = df[pitch_type_col].value_counts()
    labels = [f"{pt}: {pct:.1f}%" for pt, pct in (usage / usage.sum() * 100).items()]
    wedges, _ = ax.pie(usage, labels=None, startangle=90)
    ax.set_title("Pitch Type Usage")
    ax.legend(wedges, labels, loc='center left', bbox_to_anchor=(1, 0.5))

# Recommendation: use StrikeZonePlotter.plot_pitch_type_pie() instead for future development.

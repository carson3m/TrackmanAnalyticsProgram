
# Deprecated: plotting logic is now handled by strike_zone_plotter_cleaned.py
# File retained for backward compatibility or legacy reference.

def plot_pitch_type_pie(df, ax, pitch_type_col='AutoPitchType'):
    usage = df[pitch_type_col].value_counts()
    labels = [f"{pt}: {pct:.1f}%" for pt, pct in (usage / usage.sum() * 100).items()]
    wedges, _ = ax.pie(usage, labels=None, startangle=90)
    ax.set_title("Pitch Type Usage")
    ax.legend(wedges, labels, loc='center left', bbox_to_anchor=(1, 0.5))
    
import matplotlib.pyplot as plt

@staticmethod
def plot_summary_strike_zone(df, ax, title="Strike Zone – All Pitches"):
    strikes = df[df['IsInZone']]
    balls = df[~df['IsInZone']]

    ax.scatter(balls['PlateLocSide'], balls['PlateLocHeight'],
               color='red', label='Outside Zone', alpha=0.5)
    ax.scatter(strikes['PlateLocSide'], strikes['PlateLocHeight'],
               color='green', label='In Zone', alpha=0.5)

    ax.set_xlabel("Horizontal Location (ft)")
    ax.set_ylabel("Vertical Location (ft)")
    ax.set_title(title)

    ax.add_patch(
        plt.Rectangle((-0.83, 1.5), 1.66, 2.0, linewidth=1, edgecolor='white', facecolor='none')
    )
    ax.legend()
    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(0, 5)


# Recommendation: use StrikeZonePlotter.plot_pitch_type_pie() instead for future development.

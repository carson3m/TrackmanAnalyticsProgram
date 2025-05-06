import matplotlib.pyplot as plt
import matplotlib.patches as patches

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

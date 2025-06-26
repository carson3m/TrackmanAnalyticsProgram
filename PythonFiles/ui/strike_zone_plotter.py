
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import pandas as pd


class StrikeZonePlotter:
    def __init__(self):
        self.pitch_colors = {
            'Four-Seam': 'red',
            'Sinker': 'blue',
            'Curveball': 'green',
            'Slider': 'purple',
            'Changeup': 'orange',
            'Knuckleball': 'cyan',
            'Splitter': 'yellow'
        }

    def plot_pitch_calls(self, strikes_df, balls_df, ax):
        # Diagnostic logging
        print("Strikes before dropna:", len(strikes_df))
        print("Balls before dropna:", len(balls_df))
        # Clean NaNs for safe plotting
        strikes_df = strikes_df.dropna(subset=["plate_loc_side", "plate_loc_height"])
        balls_df = balls_df.dropna(subset=["plate_loc_side", "plate_loc_height"])

        if strikes_df.empty and balls_df.empty:
            ax.text(0.5, 0.5, "No pitch location data to plot.", ha='center', va='center', transform=ax.transAxes)
            ax.set_xlim(-2, 2)
            ax.set_ylim(1, 5)
            ax.set_title("Strike Zone Plot")
            ax.set_xlabel("Horizontal Location (ft)")
            ax.set_ylabel("Vertical Location (ft)")
            ax.grid(True)
            return
        balls_df = balls_df.dropna(subset=["plate_loc_side", "plate_loc_height"])

        # Plot strike and ball locations
        ax.scatter(
            strikes_df["plate_loc_side"],
            strikes_df["plate_loc_height"],
            color="blue", label="Strike Called", alpha=0.5
        )
        ax.scatter(
            balls_df["plate_loc_side"],
            balls_df["plate_loc_height"],
            color="red", label="Ball Called", alpha=0.5
        )

        # Calculate limits safely
        all_x = pd.concat([strikes_df["plate_loc_side"], balls_df["plate_loc_side"]], ignore_index=True)
        all_y = pd.concat([strikes_df["plate_loc_height"], balls_df["plate_loc_height"]], ignore_index=True)

        if not all_x.empty and not all_y.empty:
            x_min, x_max = all_x.min() - 0.5, all_x.max() + 0.5
            y_min, y_max = all_y.min() - 0.5, all_y.max() + 0.5
        else:
            x_min, x_max = -2.5, 2.5
            y_min, y_max = -1.0, 5.0  # allow low pitches

        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)

        # Draw strike zone (standard MLB dimensions)
        zone_x, zone_y = -0.83, 1.5
        zone_width, zone_height = 1.66, 2.0
        rect = plt.Rectangle((zone_x, zone_y), zone_width, zone_height, fill=False, color="black", lw=2)
        ax.add_patch(rect)

        ax.set_xlabel("Horizontal Location (ft)")
        ax.set_ylabel("Vertical Location (ft)")
        ax.set_title("Strike Zone Plot")
        ax.legend()

        ax.grid(True)

    def plot_pitches_by_type(self, pitches, ax, pitch_col='AutoPitchType'):
        for pitch_type in pitches[pitch_col].dropna().unique():
            pitch_data = pitches[pitches[pitch_col] == pitch_type]
            color = self.pitch_colors.get(pitch_type, 'gray')
            ax.scatter(pitch_data['plate_loc_side'], pitch_data['plate_loc_height'],
                       color=color, label=pitch_type, alpha=0.5)
        ax.set_xlabel('Horizontal Location (ft)')
        ax.set_ylabel('Vertical Location (ft)')
        ax.set_title('Pitch Locations by Type - (Pitchers View)')
        ax.set_xlim(-2, 2)
        ax.set_ylim(1, 5)
        ax.set_aspect('equal', adjustable='box')
        ax.legend()
        self.add_strike_zone(ax)

    def plot_pitch_breaks(self, df, ax, pitch_col='AutoPitchType', title='Horizontal vs Vertical Break'):
        if 'movement_horizontal' not in df.columns or 'induced_vertical' not in df.columns:
            ax.set_title("Required break columns missing")
            return
        for pitch_type in df[pitch_col].dropna().unique():
            subset = df[df[pitch_col] == pitch_type]
            color = self.pitch_colors.get(pitch_type, 'gray')
            ax.scatter(subset['movement_horizontal'], subset['induced_vertical'],
                       label=pitch_type, alpha=0.7, color=color)
        ax.axhline(0, color='gray', linestyle='--')
        ax.axvline(0, color='gray', linestyle='--')
        ax.set_xlabel('Horizontal Break (inches)')
        ax.set_ylabel('Induced Vertical Break (inches)')
        ax.set_title(title)
        ax.set_xlim(-25, 25)
        ax.set_ylim(-25, 25)
        ax.legend()
        ax.grid(True)

    def plot_spin_rate_by_type(self, df, ax, pitch_col='AutoPitchType'):
        if 'spin_rate' not in df.columns or pitch_col not in df.columns:
            ax.set_title("Spin Rate data unavailable")
            return
        palette = {pt: self.pitch_colors.get(pt, 'gray') for pt in df[pitch_col].dropna().unique()}
        sns.boxplot(data=df, x=pitch_col, y='spin_rate', ax=ax, palette=palette)
        ax.set_title("Spin Rate by Pitch Type")
        ax.set_xlabel("Pitch Type")
        ax.set_ylabel("Spin Rate (RPM)")
        ax.tick_params(axis='x', rotation=45)

    def plot_side_view_release(self, df, ax, pitch_col='AutoPitchType'):
        if 'release_extension' not in df.columns or 'release_height' not in df.columns or pitch_col not in df.columns:
            ax.set_title("Side view data unavailable")
            return

        for pitch_type in df[pitch_col].dropna().unique():
            subset = df[df[pitch_col] == pitch_type]
            color = self.pitch_colors.get(pitch_type, 'gray')
            ax.scatter(subset['release_extension'], subset['release_height'], alpha=0.6, label=pitch_type, color=color)

        ax.set_xlabel("Extension Toward Batter (ft)")
        ax.set_ylabel("Release Height (ft)")
        ax.set_title("Side View of Release by Pitch Type")
        ax.set_xlim(2.0, 8.0)
        ax.set_ylim(1.0, 7.0)
        ax.legend()
        ax.set_aspect('equal', adjustable='box')

    def plot_release_point_scatter(self, df, ax, pitch_col='AutoPitchType'):
        if 'release_height' not in df.columns or 'release_side' not in df.columns or pitch_col not in df.columns:
            ax.set_title("Release point data unavailable")
            return
        for pitch_type in df[pitch_col].dropna().unique():
            subset = df[df[pitch_col] == pitch_type]
            color = self.pitch_colors.get(pitch_type, 'gray')
            ax.scatter(subset['release_side'], subset['release_height'],
                       alpha=0.6, label=pitch_type, color=color)
        ax.set_xlabel("Release Side (ft)")
        ax.set_ylabel("Release Height (ft)")
        ax.set_title("Release Point by Pitch Type")
        ax.set_xlim(-3, 3)
        ax.set_ylim(1, 7)
        ax.legend()
        ax.set_aspect('equal', adjustable='box')

    def add_strike_zone(self, ax):
        inch_to_feet = 1 / 12.0
        width = 19.91 * inch_to_feet
        bottom = 19.47 * inch_to_feet
        height = (40.53 - 19.47) * inch_to_feet
        zone = patches.Rectangle((-width / 2, bottom), width, height,
                                 linewidth=1, edgecolor='black', facecolor='none')
        ax.add_patch(zone)
        ax.set_xlim(-2.5, 2.5)
        ax.set_ylim(0, 5)
        
def plot_umpire_calls(df, ax, zone_bounds=(-0.83, 0.83, 1.5, 3.5)):
    import matplotlib.patches as patches

    # Filter for called pitches only
    called = df[df['PitchCall'].isin(['StrikeCalled', 'BallCalled'])].copy()

    # Determine if each pitch was actually in zone
    zone_left, zone_right, zone_bottom, zone_top = zone_bounds
    in_zone = (
        (called['PlateLocSide'] >= zone_left) & (called['PlateLocSide'] <= zone_right) &
        (called['PlateLocHeight'] >= zone_bottom) & (called['PlateLocHeight'] <= zone_top)
    )

    # Add call correctness
    called['Correct'] = (
        ((called['PitchCall'] == 'StrikeCalled') & in_zone) |
        ((called['PitchCall'] == 'BallCalled') & ~in_zone)
    )

    # Tag missed 3rd strike and missed 4th ball
    if 'Balls' in df.columns and 'Strikes' in df.columns:
        called['CriticalMiss'] = (
            ((called['PitchCall'] == 'BallCalled') & in_zone & (called['Strikes'] == 2)) |  # missed 3rd strike
            ((called['PitchCall'] == 'StrikeCalled') & ~in_zone & (called['Balls'] == 3))   # missed 4th ball
        )
    else:
        called['CriticalMiss'] = False

    # Plot
    correct = called[called['Correct']]
    incorrect = called[~called['Correct']]
    critical = called[called['CriticalMiss']]

    ax.scatter(correct['PlateLocSide'], correct['PlateLocHeight'], c='green', label='Correct Call', alpha=0.5)
    ax.scatter(incorrect['PlateLocSide'], incorrect['PlateLocHeight'], c='red', label='Missed Call', alpha=0.5)
    ax.scatter(critical['PlateLocSide'], critical['PlateLocHeight'], edgecolors='black',
               facecolors='yellow', s=100, label='Critical Miss', linewidths=1.5)

    # Strike zone box
    ax.add_patch(patches.Rectangle(
        (zone_left, zone_bottom),
        zone_right - zone_left,
        zone_top - zone_bottom,
        linewidth=2,
        edgecolor='black',
        facecolor='none'
    ))

    ax.set_xlabel("PlateLocSide")
    ax.set_ylabel("PlateLocHeight")
    ax.set_title("Umpire Call Accuracy")
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax.set_xlim(-2, 2)
    ax.set_ylim(0.5, 4.5)
    ax.set_aspect('equal', adjustable='box')


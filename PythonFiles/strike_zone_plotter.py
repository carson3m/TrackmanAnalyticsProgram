
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns

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

    def plot_pitch_calls(self, strikes, balls, ax):
        ax.scatter(strikes['PlateLocSide'], strikes['PlateLocHeight'],
                   color='blue', label='Strike Called', alpha=0.5)
        ax.scatter(balls['PlateLocSide'], balls['PlateLocHeight'],
                   color='red', label='Ball Called', alpha=0.5)
        ax.set_xlabel('Horizontal Location (ft)')
        ax.set_ylabel('Vertical Location (ft)')
        ax.set_title('Strike Zone Plot')
        ax.legend()
        self.add_strike_zone(ax)

    def plot_pitches_by_type(self, pitches, ax, pitch_col='AutoPitchType'):
        for pitch_type in pitches[pitch_col].dropna().unique():
            pitch_data = pitches[pitches[pitch_col] == pitch_type]
            color = self.pitch_colors.get(pitch_type, 'gray')
            ax.scatter(pitch_data['PlateLocSide'], pitch_data['PlateLocHeight'],
                       color=color, label=pitch_type, alpha=0.5)
        ax.set_xlabel('Horizontal Location (ft)')
        ax.set_ylabel('Vertical Location (ft)')
        ax.set_title('Pitch Locations by Type')
        ax.set_xlim(-2, 2)
        ax.set_ylim(1, 5)
        ax.set_aspect('equal', adjustable='box')
        ax.legend()
        self.add_strike_zone(ax)

    def plot_pitch_breaks(self, df, ax, pitch_col='AutoPitchType', title='Horizontal vs Vertical Break'):
        if 'HorzBreak' not in df.columns or 'InducedVertBreak' not in df.columns:
            ax.set_title("Required break columns missing")
            return
        for pitch_type in df[pitch_col].dropna().unique():
            subset = df[df[pitch_col] == pitch_type]
            color = self.pitch_colors.get(pitch_type, 'gray')
            ax.scatter(subset['HorzBreak'], subset['InducedVertBreak'],
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
        if 'SpinRate' not in df.columns or pitch_col not in df.columns:
            ax.set_title("Spin Rate data unavailable")
            return
        palette = {pt: self.pitch_colors.get(pt, 'gray') for pt in df[pitch_col].dropna().unique()}
        sns.boxplot(data=df, x=pitch_col, y='SpinRate', ax=ax, palette=palette)
        ax.set_title("Spin Rate by Pitch Type")
        ax.set_xlabel("Pitch Type")
        ax.set_ylabel("Spin Rate (RPM)")
        ax.tick_params(axis='x', rotation=45)

    def plot_side_view_release(self, df, ax, pitch_col='AutoPitchType'):
        if 'Extension' not in df.columns or 'RelHeight' not in df.columns or pitch_col not in df.columns:
            ax.set_title("Side view data unavailable")
            return

        for pitch_type in df[pitch_col].dropna().unique():
            subset = df[df[pitch_col] == pitch_type]
            color = self.pitch_colors.get(pitch_type, 'gray')
            ax.scatter(subset['Extension'], subset['RelHeight'], alpha=0.6, label=pitch_type, color=color)

        ax.set_xlabel("Extension Toward Batter (ft)")
        ax.set_ylabel("Release Height (ft)")
        ax.set_title("Side View of Release by Pitch Type")
        ax.set_xlim(2.0, 8.0)
        ax.set_ylim(1.0, 7.0)
        ax.legend()
        ax.set_aspect('equal', adjustable='box')

    def plot_release_point_scatter(self, df, ax, pitch_col='AutoPitchType'):
        if 'RelHeight' not in df.columns or 'RelSide' not in df.columns or pitch_col not in df.columns:
            ax.set_title("Release point data unavailable")
            return
        for pitch_type in df[pitch_col].dropna().unique():
            subset = df[df[pitch_col] == pitch_type]
            color = self.pitch_colors.get(pitch_type, 'gray')
            ax.scatter(subset['RelSide'], subset['RelHeight'],
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

import matplotlib.pyplot as plt
import pandas as pd
from PythonFiles.utils.summary_helpers import get_pitch_type_column


class PlayerMetricsAnalyzer:
    def __init__(self, df, name, zone_bounds=(-0.83, 0.83, 1.5, 3.5)):
        self.df = df.copy()
        self.name = name
        self.zone_bounds = zone_bounds
        self.normalize_pitch_calls()
        self.rename_columns()
        self.pitch_type_col = self.get_pitch_type_column()
        if self.pitch_type_col in self.df.columns:
            self.df = self.df[self.df[self.pitch_type_col].notna() & (self.df[self.pitch_type_col].str.strip() != "")]


    def normalize_pitch_calls(self):
        pitchcall_map = {
            'StrikeSwinging': 'SwingMiss',
            'FoulBallNotFieldable': 'FoulBall',
            'FoulBallFieldable': 'FoulBall',
            'BallinDirt': 'BallCalled'
        }
        self.df['PitchCall'] = self.df['PitchCall'].replace(pitchcall_map)

    def rename_columns(self):
        if 'Angle' in self.df.columns and 'LaunchAngle' not in self.df.columns:
            self.df.rename(columns={'Angle': 'LaunchAngle'}, inplace=True)

    def get_pitch_type_column(self):
        return 'AutoPitchType' if 'AutoPitchType' in self.df.columns else 'TaggedPitchType'

    def command_metrics_string(self):
        cols = ['PitchofPA', 'PitchCall', 'Inning', 'Top/Bottom', 'PAofInning']
        if not all(col in self.df.columns for col in cols):
            return "Required columns missing for command metrics."

        self.df['AtBatID'] = self.df['Inning'].astype(str) + '_' + self.df['Top/Bottom'] + '_' + self.df['PAofInning'].astype(str)
        first_pitches = self.df[self.df['PitchofPA'] == 1]
        first_pitch_strikes = first_pitches[first_pitches['PitchCall'].isin(['StrikeCalled', 'InPlay'])]
        total_fp = len(first_pitches)
        strikes_fp = len(first_pitch_strikes)
        fp_strike_pct = (strikes_fp / total_fp * 100) if total_fp > 0 else 0

        strike_calls = self.df[self.df['PitchCall'].isin(['StrikeCalled', 'InPlay', 'FoulBall', 'SwingMiss'])]
        strike_pct = (len(strike_calls) / len(self.df)) * 100 if len(self.df) > 0 else 0

        summary = f"\n🎯 Command Metrics for {self.name}\n"
        summary += f"Total Pitches: {len(self.df)}\n"
        summary += f"First-Pitch Strike %: {fp_strike_pct:.2f}%\n"
        summary += f"Overall Strike %: {strike_pct:.2f}%\n"
        return summary

    def avg_velocity_string(self):
        if 'RelSpeed' not in self.df.columns:
            return ""
        if self.pitch_type_col not in self.df.columns:
            return "Pitch type column missing."

        avg_speeds = self.df.groupby(self.pitch_type_col)['RelSpeed'].mean().sort_values()
        summary = "\nAvg Velocities:\n" + "\n".join(f"- {pt}: {v:.1f} mph" for pt, v in avg_speeds.items())
        return summary

    def result_metrics_string(self):
        df = self.df
        required = ['PitchCall', 'PlateLocSide', 'PlateLocHeight', 'ExitSpeed', 'LaunchAngle']
        missing = [col for col in required if col not in df.columns]
        if missing:
            return f"\n⚠️ Skipped result-driven metrics — missing: {', '.join(missing)}"

        swings = df[df['PitchCall'].isin(['SwingMiss', 'FoulBall', 'InPlay'])]
        whiffs = df[df['PitchCall'] == 'SwingMiss']
        contacts = df[df['PitchCall'].isin(['FoulBall', 'InPlay'])]
        balls_in_play = df[df['PitchCall'] == 'InPlay']
        hard_hits = balls_in_play[balls_in_play['ExitSpeed'] >= 95]
        barrels = balls_in_play[
            (balls_in_play['ExitSpeed'] >= 98) &
            (balls_in_play['LaunchAngle'].between(26, 30))
        ]

        zone_left, zone_right, zone_bottom, zone_top = self.zone_bounds
        in_zone = df[
            (df['PlateLocSide'] >= zone_left) & (df['PlateLocSide'] <= zone_right) &
            (df['PlateLocHeight'] >= zone_bottom) & (df['PlateLocHeight'] <= zone_top)
        ]
        out_zone = df.drop(in_zone.index)
        chases = out_zone[out_zone['PitchCall'].isin(['SwingMiss', 'FoulBall', 'InPlay'])]

        has_strikes = 'Strikes' in df.columns
        if has_strikes:
            two_strike = df[df['Strikes'] == 2]
            putaway_pitches = two_strike[two_strike['PitchCall'] == 'SwingMiss']
            putaway_pct = (len(putaway_pitches) / len(two_strike) * 100) if len(two_strike) > 0 else 0
        else:
            putaway_pct = None

        shadow_zone = df[
            ((df['PlateLocSide'].between(zone_left - 0.5, zone_left) |
              df['PlateLocSide'].between(zone_right, zone_right + 0.5)) &
             df['PlateLocHeight'].between(zone_bottom - 0.5, zone_top + 0.5)) |
            ((df['PlateLocHeight'].between(zone_bottom - 0.5, zone_bottom) |
              df['PlateLocHeight'].between(zone_top, zone_top + 0.5)) &
             df['PlateLocSide'].between(zone_left - 0.5, zone_right + 0.5))
        ]
        shadow_zone_pct = (len(shadow_zone) / len(df) * 100) if len(df) > 0 else 0

        summary = f"\n"
        summary += f"\n⚡ Result-Driven Metrics for {self.name}\n"
        summary += f"Whiff Rate: {(len(whiffs)/len(swings)*100 if len(swings)>0 else 0):.2f}%\n"
        summary += f"Contact Rate: {(len(contacts)/len(swings)*100 if len(swings)>0 else 0):.2f}%\n"
        summary += f"Hard Hit %: {(len(hard_hits)/len(balls_in_play)*100 if len(balls_in_play)>0 else 0):.2f}%\n"
        summary += f"Barrel %: {(len(barrels)/len(balls_in_play)*100 if len(balls_in_play)>0 else 0):.2f}%\n"
        summary += f"Chase Rate: {(len(chases)/len(out_zone)*100 if len(out_zone)>0 else 0):.2f}%\n"
        summary += f"PutAway %: {(f'{putaway_pct:.2f}%' if putaway_pct is not None else 'N/A (no Strikes column)')}\n"
        summary += f"Shadow Zone %: {shadow_zone_pct:.2f}%\n"
        return summary

    def full_summary_string(self):
        return (
            self.command_metrics_string() +
            self.avg_velocity_string() +
            self.result_metrics_string()
        )
    @staticmethod
    def format_val(val, decimals=1):
        return round(val, decimals) if isinstance(val, (float, int)) else val

    def plot_pitch_type_pie(self, ax, pitch_colors=None):
        usage = self.df[self.pitch_type_col].value_counts()
        labels = usage.index.tolist()
        values = usage.values.tolist()

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

    def plot_pitch_type_bar(self, ax):
        if self.pitch_type_col not in self.df.columns:
            ax.set_title("No pitch type column")
            return
        counts = self.df[self.pitch_type_col].value_counts()
        ax.bar(counts.index, counts.values)
        ax.set_xticklabels(counts.index, rotation=45)
        ax.set_title("Pitch Type Count")
        ax.set_ylabel("Count")
        
    def per_pitch_type_metrics_df(self):
        df = self.df
        if self.pitch_type_col not in df.columns:
            return pd.DataFrame()

        rows = []
        zone_left, zone_right, zone_bottom, zone_top = self.zone_bounds
        has_strikes = 'Strikes' in df.columns

        for pitch, group in df.groupby(self.pitch_type_col):
            swings = group[group['PitchCall'].isin(['SwingMiss', 'FoulBall', 'InPlay'])]
            whiffs = group[group['PitchCall'] == 'SwingMiss']
            contacts = group[group['PitchCall'].isin(['FoulBall', 'InPlay'])]
            balls_in_play = group[group['PitchCall'] == 'InPlay']
            strikes = group[group['PitchCall'].isin(['StrikeCalled', 'SwingMiss', 'FoulBall', 'InPlay'])]
            out_zone = group[
                (group['PlateLocSide'] < zone_left) | (group['PlateLocSide'] > zone_right) |
                (group['PlateLocHeight'] < zone_bottom) | (group['PlateLocHeight'] > zone_top)
            ]
            chases = out_zone[out_zone['PitchCall'].isin(['SwingMiss', 'FoulBall', 'InPlay'])]
            in_zone = group[
                (group['PlateLocSide'].between(zone_left, zone_right)) &
                (group['PlateLocHeight'].between(zone_bottom, zone_top))
            ]
            hard_hits = balls_in_play[balls_in_play['ExitSpeed'] >= 95]
            barrels = balls_in_play[
                (balls_in_play['ExitSpeed'] >= 98) &
                (balls_in_play['LaunchAngle'].between(26, 30))
            ]

            if has_strikes:
                two_strike = group[group['Strikes'] == 2]
                putaways = two_strike[two_strike['PitchCall'] == 'SwingMiss']
                putaway_pct = (len(putaways) / len(two_strike) * 100) if len(two_strike) > 0 else None
            else:
                putaway_pct = None

            avg_ext = group['Extension'].mean() if 'Extension' in group.columns else None

            rows.append({
                'Pitch Type': pitch,
                'Count': len(group),
                'Avg Velo': self.format_val(group['RelSpeed'].mean() if 'RelSpeed' in group.columns else None),
                'Spin Rate': self.format_val(group['SpinRate'].mean() if 'SpinRate' in group.columns else None),
                'Vert. Break': self.format_val(group.get('InducedVertBreak', group.get('VertBreak')).mean() if 'InducedVertBreak' in group.columns or 'VertBreak' in group.columns else None),
                'Horz. Break': self.format_val(group['HorzBreak'].mean() if 'HorzBreak' in group.columns else None),
                'Strike %': self.format_val(len(strikes) / len(group) * 100 if len(group) > 0 else 0),
                'Whiff %': self.format_val(len(whiffs) / len(swings) * 100 if len(swings) > 0 else 0),
                'Chase %': self.format_val(len(chases) / len(out_zone) * 100 if len(out_zone) > 0 else 0),
                'Contact %': self.format_val(len(contacts) / len(swings) * 100 if len(swings) > 0 else 0),
                'Hard Hit %': self.format_val(len(hard_hits) / len(balls_in_play) * 100 if len(balls_in_play) > 0 else 0),
                'Barrel %': self.format_val(len(barrels) / len(balls_in_play) * 100 if len(balls_in_play) > 0 else 0),
                'PutAway %': self.format_val(putaway_pct if putaway_pct is not None else "N/A"),
                'In-Zone %': self.format_val(len(in_zone) / len(group) * 100 if len(group) > 0 else 0),
                'Avg Extension': self.format_val(avg_ext)
            })

        return pd.DataFrame(rows).sort_values(by='Whiff %', ascending=False)

    def umpire_accuracy_string(self):
        df = self.df
        if not all(col in df.columns for col in ['PitchCall', 'PlateLocSide', 'PlateLocHeight']):
            return "\n⚠️ Umpire accuracy not available — missing location or call data."

        zone_left, zone_right, zone_bottom, zone_top = self.zone_bounds

        called = df[df['PitchCall'].isin(['StrikeCalled', 'BallCalled'])]
        in_zone = called[
            (called['PlateLocSide'] >= zone_left) & (called['PlateLocSide'] <= zone_right) &
            (called['PlateLocHeight'] >= zone_bottom) & (called['PlateLocHeight'] <= zone_top)
        ]
        out_zone = called.drop(in_zone.index)

        correct_strikes = in_zone[in_zone['PitchCall'] == 'StrikeCalled']
        missed_balls = in_zone[in_zone['PitchCall'] == 'BallCalled']
        correct_balls = out_zone[out_zone['PitchCall'] == 'BallCalled']
        missed_strikes = out_zone[out_zone['PitchCall'] == 'StrikeCalled']

        total_calls = len(called)
        correct_calls = len(correct_strikes) + len(correct_balls)
        accuracy = (correct_calls / total_calls * 100) if total_calls > 0 else 0

        return (
            f"\nUmpire Accuracy Metrics\n"
            f"Total Called Pitches: {total_calls}\n"
            f"Correct Strikes: {len(correct_strikes)}\n"
            f"Correct Balls: {len(correct_balls)}\n"
            f"Missed Strikes: {len(missed_strikes)}\n"
            f"Missed Balls: {len(missed_balls)}\n"
            f"Overall Accuracy: {accuracy:.2f}%"
        )




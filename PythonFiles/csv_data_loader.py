import pandas as pd
import matplotlib.pyplot as plt
class CSVDataLoader:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.df = self.load_csv()
    
    def load_csv(self):
        return pd.read_csv(self.csv_file)
    
    def get_pitch_calls(self, call_type):
        if call_type in self.df['PitchCall'].unique():
            return self.df[self.df['PitchCall'] == call_type]
        else:
            print(f"Warning: {call_type} not found in data")
            return pd.DataFrame()
    
    def get_pitcher_stats(self, pitcher_name):
        pitcher_data = self.df[self.df['Pitcher'] == pitcher_name]
        
        strike_calls = ['StrikeCalled', 'StrikeSwinging', 'FoulBallNotFieldable', 'FoulBallFieldable', 'InPlay']
        ball_calls = ['BallCalled', 'BallinDirt', 'HitByPitch']
        
        total_pitches = len(pitcher_data)
        strikes = len(pitcher_data[pitcher_data['PitchCall'].isin(strike_calls)])
        balls = len(pitcher_data[pitcher_data['PitchCall'].isin(ball_calls)])
        
        strike_percentage = (strikes / total_pitches) * 100 if total_pitches > 0 else 0
        return {'total_pitches': total_pitches,
                'strikes': strikes,
                'balls': balls,
                'strike_percentage': strike_percentage
                }
    def get_pitch_type_data(self, pitch_type):
        pitch_data = self.df[self.df['PitchType']==pitch_type]
        return pitch_data
    
    def plot_pitch_type(self, pitch_type):
        pitch_data = self.get_pitch_type_data(pitch_type)
        plt.scatter(pitch_data['PlateLocSide'], pitch_data['PlateLocHeight'], label=f'{pitch_type} Pitches', alpha=0.5)
        plt.title(f'{pitch_type} Pitch Locations')
        plt.xlabel('Plate Location Side (feet)')
        plt.ylabel('Plate Location Height (feet)')
        plt.legend()
        plt.show()
        
    def get_pitcher_extended_stats(self, pitcher_name):
        pitcher_data = self.df[self.df['Pitcher'] == pitcher_name]
        
    def get_dataframe(self):
        return self.df
        
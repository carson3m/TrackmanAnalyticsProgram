import matplotlib.pyplot as plt
import matplotlib.patches as patches

class StrikeZonePlotter:
    def __init__(self):
        self.figure, self.ax = plt.subplots(figsize=(12,6))
        
    def plot_pitch_calls(self, strikes, balls): 
        self.ax.scatter(strikes['PlateLocSide'], strikes['PlateLocHeight'], color='blue', label='Strike Called', alpha=0.5)
        self.ax.scatter(balls['PlateLocSide'], balls['PlateLocHeight'], color='red', label='Ball Called', alpha=0.5)
        
    def plot_pitches_thrown(self, pitches):
        pitch_colors = {
            'Four-Seam': 'red',
            'Sinker': 'blue',
            'Curveball': 'green',
            'Slider': 'purple',
            'Changeup': 'orange',
            'Knuckleball': 'cyan',
            'Splitter': 'yellow',
            # Add more pitch types and their colors as needed
        }
        
        # Plot each pitch type with its corresponding color
        for pitch_type in pitches['AutoPitchType'].unique():
            pitch_data = pitches[pitches['AutoPitchType'] == pitch_type]
            color = pitch_colors.get(pitch_type, 'gray')  # Default to gray if pitch type not in the map
            self.ax.scatter(pitch_data['PlateLocSide'], pitch_data['PlateLocHeight'], color=color, label=pitch_type, alpha=0.5)
        

        
    def add_strike_zone(self):
        inch_to_feet = 1/12.0
        inner_width = 19.91* inch_to_feet
        inner_bottom = 19.47*inch_to_feet
        inner_top = 40.53 * inch_to_feet
        
        inner_rect = patches.Rectangle(
            (-inner_width / 2, inner_bottom),
            inner_width,
            inner_top - inner_bottom,
            linewidth=2, edgecolor='green', facecolor='none',
            label = "Strike Zone" 
        )
        
        self.ax.add_patch(inner_rect)
        
    def finalize_plot(self, title):
        self.ax.set_title(title)
        self.ax.set_xlabel('Plate Location Side (feet)')
        self.ax.set_ylabel('Plate Location Height (feet)')
        self.ax.set_xlim(-5, 5)
        self.ax.set_ylim(0, 5)
        self.ax.grid(False)
        self.ax.legend()
        
    def show(self):
        plt.show()
        
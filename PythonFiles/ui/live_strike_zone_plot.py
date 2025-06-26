from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from ui.strike_zone_plotter import StrikeZonePlotter  # Your class lives here
import pandas as pd

class LiveStrikeZonePlot(QWidget):
    def __init__(self):
        super().__init__()
        self.plotter = StrikeZonePlotter()
        self.figure = Figure(figsize=(4, 4))
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def update_plot(self, df: pd.DataFrame):
        self.ax.clear()
        if df.empty:
            self.ax.text(0.5, 0.5, "No pitch location data to plot.", ha='center', va='center', transform=self.ax.transAxes)
        else:
            # Use auto-classified pitch type and location
            StrikeZonePlotter().plot_pitches_by_type(df, self.ax, pitch_col='AutoPitchType')
        self.canvas.draw()


from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from core.player_metrics import PlayerMetricsAnalyzer
from ui.strike_zone_plotter import plot_umpire_calls

class UmpireAccuracyWidget(QWidget):
    def __init__(self, df, back_callback):
        super().__init__()
        self.df = df.copy()
        self.layout = QVBoxLayout()

        self.accuracy_text = QTextEdit()
        self.accuracy_text.setReadOnly(True)
        self.accuracy_text.setMinimumHeight(150)

        analyze_btn = QPushButton("Calculate Umpire Accuracy")
        analyze_btn.clicked.connect(self.calculate_accuracy)

        back_btn = QPushButton("Back to Menu")
        back_btn.clicked.connect(back_callback)

        self.layout.addWidget(QLabel("Umpire Accuracy Analyzer"))
        self.layout.addWidget(analyze_btn)
        self.layout.addWidget(self.accuracy_text)
        self.layout.addWidget(back_btn)

        self.setLayout(self.layout)

    def calculate_accuracy(self):
        analyzer = PlayerMetricsAnalyzer(self.df, name="All Pitches")
        self.accuracy_text.setText(analyzer.umpire_accuracy_string())
        fig, ax = plt.subplots(figsize=(6, 6))
        plot_umpire_calls(self.df, ax)
        canvas = FigureCanvas(fig)
        self.layout.addWidget(canvas)

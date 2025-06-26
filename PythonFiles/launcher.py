# launcher.py
from PyQt5.QtWidgets import QApplication, QFileDialog
import pandas as pd
import sys
from ui.main_window import MainWindow

def launch_csv_mode():
    app = QApplication(sys.argv)
    file_dialog = QFileDialog()
    file_path, _ = file_dialog.getOpenFileName(None, "Select CSV", "", "CSV Files (*.csv)")
    if not file_path:
        print("No file selected. Exiting.")
        return
    df = pd.read_csv(file_path)
    window = MainWindow(df, live=False)
    window.show()
    sys.exit(app.exec_())

def launch_live_mode():
    app = QApplication(sys.argv)
    df = pd.DataFrame()  # Start empty
    window = MainWindow(df, live=True)
    window.show()
    sys.exit(app.exec_())


import tkinter as tk
import matplotlib
matplotlib.use('TkAgg')
from tkinter import filedialog
from PythonFiles.csv_data_loader import CSVDataLoader
from PythonFiles.player_selection_ui import PlayerSelectionUI

def main():
    # Create a temporary root to use file dialog
    temp_root = tk.Tk()
    temp_root.withdraw()
    file_path = filedialog.askopenfilename(title="Select CSV Data File", filetypes=[("CSV Files", "*.csv")])
    temp_root.destroy()

    if not file_path:
        print("No file selected. Exiting.")
        return

    # Load the CSV data
    loader = CSVDataLoader(file_path)

    # Start full GUI with PlayerSelectionUI
    root = tk.Tk()
    root.title("Baseball Player Summary Analysis")
    root.geometry("900x700")

    ui = PlayerSelectionUI(loader)
    ui.launch(root)

    root.mainloop()

if __name__ == "__main__":
    main()

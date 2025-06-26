import tkinter as tk
from tkinter import filedialog, messagebox
from csv_data_loader import CSVDataLoader

class FileSelectorUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Trackman Data Viewer")
        self.root.geometry("1200x800")

        self.loader = None

        self.label = tk.Label(self.root, text="Select a CSV file to analyze:")
        self.label.pack(pady=10)

        self.button = tk.Button(self.root, text="Browse", command=self.browse_file)
        self.button.pack()

        self.selected_file = None

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.loader = CSVDataLoader(file_path)
            self.display_pitcher_selection()

    def run(self):
        self.root.mainloop()
        return self.selected_file

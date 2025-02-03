import pandas as pd
import re
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def list_columns(file_path):
    """
    Reads the CSV file (semicolon-delimited) and prints each column with its index.
    Returns the DataFrame.
    """
    try:
        df = pd.read_csv(file_path, sep=";", encoding="utf-8", on_bad_lines='skip')
        print("List of columns:")
        for idx, col in enumerate(df.columns, start=1):
            print(f"{idx}: {col}")
        return df
    except Exception as e:
        print("Error reading CSV file:", e)
        return None

def count_occurrences_in_scbs(df):
    """
    Counts occurrences of the following exact strings in the 'Scbs' column:
      - "¤¤¤ 1: Naturvetenskap"
      - "¤¤¤ 3: Medicin och hälsovetenskap"
      - "¤¤¤ 2: Teknik"
    """
    if 'Scbs' not in df.columns:
        print("Error: The file does not contain a 'Scbs' column.")
        return

    # Initialize counters for each pattern
    count_natur = 0
    count_medicin = 0
    count_teknik = 0

    # Define the patterns using re.escape to match the strings literally
    pattern_natur    = re.escape("¤¤¤ 1: Naturvetenskap")
    pattern_medicin  = re.escape("¤¤¤ 3: Medicin och hälsovetenskap")
    pattern_teknik   = re.escape("¤¤¤ 2: Teknik")

    # Iterate through each value in the 'Scbs' column
    for i, value in enumerate(df["Scbs"]):
        if isinstance(value, str):
            count_natur    += len(re.findall(pattern_natur, value))
            count_medicin  += len(re.findall(pattern_medicin, value))
            count_teknik   += len(re.findall(pattern_teknik, value))
    
    print("\nPattern Occurrence Counts in 'Scbs' Column:")
    print(f"Occurrences of '¤¤¤ 1: Naturvetenskap': {count_natur}")
    print(f"Occurrences of '¤¤¤ 3: Medicin och hälsovetenskap': {count_medicin}")
    print(f"Occurrences of '¤¤¤ 2: Teknik': {count_teknik}")

def load_file_and_process():
    # Hide the Tkinter root window
    Tk().withdraw()
    
    # Open a file dialog to select a CSV file
    file_path = askopenfilename(
        title="Select CSV File", 
        filetypes=[("CSV Files", "*.csv")]
    )
    
    if file_path:
        # List all columns and retrieve the DataFrame
        df = list_columns(file_path)
        if df is not None:
            # Count occurrences in the 'Scbs' column
            count_occurrences_in_scbs(df)
    else:
        print("No file selected.")

if __name__ == "__main__":
    load_file_and_process()

# After running the file it will ask for teh CSV file you wanna look trough.
# then in the terminal it will list all the COLUMNS and titles and occurence of the predetermined main 3 themes.
#  these results will show up in the terminal below
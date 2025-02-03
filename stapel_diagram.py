import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
import re

# Keywords to check for (Swedish only)
KEYWORDS = {
    'Naturvetenskap': 'naturvetenskap',
    'Medicin och Hälsovetenskap': 'medicin',
    'Teknik': 'teknik'
}

class CSVViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Data Viewer & Project Counter")
        self.root.geometry("1200x700")
        
        # Load CSV Button
        self.load_button = tk.Button(root, text="Load CSV File", command=self.load_csv)
        self.load_button.pack(pady=10)
        
        # Quit Button in top-right corner
        self.quit_button = tk.Button(root, text="Quit", command=root.quit)
        self.quit_button.pack(pady=10, anchor='ne')
        
        self.data = None  # Will hold the DataFrame
        
    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return
        
        try:
            # Load the CSV file
            self.data = pd.read_csv(file_path, sep=None, engine='python', encoding="utf-8", on_bad_lines='skip')
            messagebox.showinfo("Success", "CSV file loaded successfully!")
            self.check_columns()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV file:\n{e}")

    def check_columns(self):
        if self.data is None:
            messagebox.showerror("Error", "No data loaded.")
            return
        
        # Ensure that the last column is present
        num_columns = len(self.data.columns)
        if num_columns < 28:  # We expect 28 columns (0-indexed, so column 27 is the last one)
            messagebox.showerror("Error", "The CSV file does not have 28 columns. Please check the file.")
            return
        
        # Proceed with the project counting if column exists
        self.count_and_visualize_projects()

    def preprocess_text(self, text):
        """Preprocess the text by removing unwanted characters and keeping only Swedish words."""
        # Remove non-Swedish words, numbers, and special characters (e.g., ¤¤¤, :).
        # Only keep letters (a-z, A-Z) and spaces.
        text = re.sub(r'[^a-zA-ZåäöÅÄÖ\s:]', '', text)  # Allow Swedish letters and spaces, but remove : and special chars
        return text.lower()  # Convert to lowercase

    def extract_first_word_after_colon(self, text):
        """Extract the first word after the first colon ':' in the text."""
        # Preprocess the text to clean it
        text = self.preprocess_text(text)
        
        # Check if there is a colon in the text
        if ":" in text:
            # Split the text by the first colon and get the part after it
            text_after_colon = text.split(":", 1)[1].strip()  # Strip any extra spaces after the colon
            
            # Extract the first word (the first word directly after the colon)
            words = text_after_colon.split()  # Split into words
            if words:
                return words[0]  # Return the first word after the colon
        
        return None  # Return None if no word is found after the colon

    def match_theme(self, text):
        """Match the project description to a theme based only on the first word after the colon."""
        first_word = self.extract_first_word_after_colon(text)
        
        if first_word:
            # Match with predefined keywords
            if first_word == 'naturvetenskap':
                return 'Naturvetenskap'
            elif first_word == 'medicin':
                return 'Medicin och Hälsovetenskap'
            elif first_word == 'teknik':
                return 'Teknik'
        
        # Return None if no matching theme is found
        return None

    def count_and_visualize_projects(self):
        if self.data is None:
            messagebox.showerror("Error", "No data loaded.")
            return
        
        theme_counts = {'Naturvetenskap': 0, 'Medicin och Hälsovetenskap': 0, 'Teknik': 0}
        
        # Check if there are any completely empty rows
        empty_row_count = self.data.isnull().all(axis=1).sum()
        if empty_row_count > 0:
            messagebox.showerror("Error", f"The CSV file contains {empty_row_count} completely empty rows. The process will now end.")
            return
        
        # Loop through each row, classify the project, and count occurrences
        for index, row in self.data.iterrows():
            text = str(row['Scbs'])  # Get text from the "Scbs" column
            theme = self.match_theme(text)  # Classify the project into a theme
            
            if theme:  # If theme is found
                theme_counts[theme] += 1
        
        # Summarize the counts and show a message box
        total_projects = sum(theme_counts.values())
        messagebox.showinfo("Summary", f"Total Projects: {total_projects}\n"
                                      f"Naturvetenskap: {theme_counts['Naturvetenskap']}\n"
                                      f"Medicin och Hälsovetenskap: {theme_counts['Medicin och Hälsovetenskap']}\n"
                                      f"Tecnisk: {theme_counts['Teknik']}")

        # Create the bar chart (stapel diagram)
        self.plot_stapel_diagram(theme_counts)

    def plot_stapel_diagram(self, theme_counts):
        categories = list(theme_counts.keys())
        counts = list(theme_counts.values())
        
        # Create the bar chart with larger y-axis range
        plt.figure(figsize=(10, 6))
        plt.bar(categories, counts, color=['skyblue', 'lightgreen', 'salmon'])
        
        # Add labels and title
        plt.xlabel('Themes')
        plt.ylabel('Number of Projects')
        plt.title('Number of Projects in Each Theme')

        # Add the count labels on top of the bars
        for i, count in enumerate(counts):
            plt.text(i, count + 50, str(count), ha='center', va='bottom', fontweight='bold')

        # Display the total count at the bottom of the chart
        total_projects = sum(counts)
        plt.text(1, total_projects + 500, f"Total: {total_projects}", ha='center', va='bottom', fontsize=12, fontweight='bold')

        # Adjust y-axis limits to make sure bars don't overlap and fit within total project count
        plt.ylim(0, total_projects + 1000)  # Extend y-axis to be higher than total projects to give room

        # Adjust layout to avoid clipping of labels and titles
        plt.subplots_adjust(bottom=0.2, top=0.9)
        
        # Show the plot
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVViewerApp(root)
    root.mainloop() 


    # The code will open the GUI. press the "load in CSV file button" the look for teh csv file you wanna use.
    # then press ok on teh SUCCES window, the on OK on teh summary window. to quit press teh QUIT button from the first window
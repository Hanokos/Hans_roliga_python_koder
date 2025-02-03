import pandas as pd
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, Toplevel
from pandastable import Table
import threading
from sklearn.feature_extraction.text import TfidfVectorizer
import tkinter.font as tkFont

class CSVViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Data Viewer & Sorter")
        self.root.geometry("1200x700")
        
        # Load CSV Button
        self.load_button = tk.Button(root, text="Load CSV File", command=self.load_csv)
        self.load_button.pack(pady=10)
        
        # Quit Button in top-right corner
        self.quit_button = tk.Button(root, text="Quit", command=root.quit)
        self.quit_button.pack(pady=10, anchor='ne')
        
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        self.data = None  # Will hold the DataFrame
        self.table = None  # Will hold the pandastable Table object
        
        # Sorting Frame
        self.sorting_frame = tk.Frame(root)
        self.sorting_frame.pack(pady=5)

        # Label and Sort Dropdown
        self.sort_label = tk.Label(self.sorting_frame, text="Sort by:")
        self.sort_label.pack(side=tk.LEFT)
        
        self.sort_var = tk.StringVar()
        self.sort_dropdown = ttk.Combobox(self.sorting_frame, textvariable=self.sort_var, state="readonly")
        self.sort_dropdown.pack(side=tk.LEFT)
        
        # Sort Button
        self.sort_button = tk.Button(self.sorting_frame, text="Sort", command=self.sort_data)
        self.sort_button.pack(side=tk.LEFT, padx=5)

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return
        
        try:
            # Load the CSV file
            self.data = pd.read_csv(file_path, sep=None, engine='python', encoding="utf-8", on_bad_lines='skip')
            messagebox.showinfo("Success", "CSV file loaded successfully!")
            self.show_data()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV file:\n{e}")

    def show_data(self):
        # Clear any existing table from the frame
        for widget in self.frame.winfo_children():
            widget.destroy()
        
        # Create the pandastable table in read-only mode
        self.table = Table(self.frame, dataframe=self.data, showtoolbar=False, showstatusbar=False, editable=False)
        self.table.show()

        # Populate the dropdown with column names (only when data is loaded)
        if self.data is not None:
            columns = list(self.data.columns)
            self.sort_dropdown['values'] = columns
            
            # Bind the double-click event on the table to open project details
            self.table.bind('<Double-Button-1>', self.on_row_double_click)

    def on_row_double_click(self, event):
        """Handle double-click event to show project details"""
        row = self.table.get_row_clicked(event)
        if row is not None:
            try:
                project = self.data.iloc[row]
                self.show_project_details(project)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to retrieve project details:\n{e}")

    def sort_data(self):
        if self.data is None:
            return
        column = self.sort_var.get()
        if column:
            threading.Thread(target=self.perform_sort, args=(column,), daemon=True).start()

    def perform_sort(self, column):
        try:
            self.data = self.data.sort_values(by=column, ascending=True)
            # Refresh table with sorted data
            self.show_data()
        except Exception as e:
            messagebox.showerror("Sorting Error", f"Failed to sort:\n{e}")

    def show_project_details(self, project):
        """Show project details in a new window with key information and a short NLP summary."""
        details_window = Toplevel(self.root)
        details_window.geometry("500x400")  # Default small size
        
        # Define base font sizes
        base_title_size = 12
        base_info_size = 10

        # Define fonts
        title_font = tkFont.Font(family="Helvetica", size=base_title_size, weight="bold")
        info_font = tkFont.Font(family="Helvetica", size=base_info_size)

        # Retrieve project details
        title = project.get('ProjectTitleEn', 'N/A')
        description = project.get('ProjectAbstractEn', 'N/A')
        funding = project.get('FundingsSek', 'N/A')
        if funding != 'N/A':
            funding = f"{funding} SEK"  # Append SEK to show currency
        
        # Generate a keyword summary
        summary = self.generate_summary(description) if description.strip() != "" and description != 'N/A' else "No summary available."
        
        # Prepare the information text
        info_text = f"Project Description:\n{description}\n\n"
        info_text += f"Funding Cost: {funding}\n\n"
        info_text += f"Keyword Summary: {summary}"
        
        # Create title label
        title_label = tk.Label(details_window, text=title, font=title_font, justify=tk.CENTER)
        title_label.pack(pady=(15, 10))
        
        # Create information label
        info_label = tk.Label(details_window, text=info_text, font=info_font, justify=tk.LEFT, wraplength=450)
        info_label.pack(padx=15, pady=10)

        def adjust_font(event):
            """Dynamically change font size when window is resized."""
            width, height = event.width, event.height
            if width > 600 and height > 450:  # Check if window is larger
                title_font.config(size=16)  # Increase title font
                info_font.config(size=12)  # Increase info font
            else:
                title_font.config(size=base_title_size)  # Reset title font
                info_font.config(size=base_info_size)  # Reset info font
        
        details_window.bind("<Configure>", adjust_font)  # Bind the resize event

    def generate_summary(self, text):
        """Generate a summary using TF-IDF to extract key keywords."""
        try:
            tfidf = TfidfVectorizer(stop_words='english', max_features=10)
            tfidf_matrix = tfidf.fit_transform([text])
            feature_names = tfidf.get_feature_names_out()
            dense = tfidf_matrix.todense()
            keywords = dense.tolist()[0]

            # Pair each keyword with its TF-IDF score, sort in descending order, and select the top keywords
            sorted_keywords = sorted(zip(keywords, feature_names), reverse=True)
            top_keywords = [word for score, word in sorted_keywords if score > 0]
            return ', '.join(top_keywords[:10])
        except Exception as e:
            return f"Error generating summary: {e}"

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVViewerApp(root)
    root.mainloop()

# press the "load CSV file" button. then press ok on teh SUCCES window. then a window that is white will show up.
# OBS! very important to scroll for som reason to make the data show up. then you can either use teh tab below to sort or press on the first row with titles that is dark gray to sort.
# a row represent one project, if you press any row/project it will give you another window with some extra information about the project. for full text make it full screen.
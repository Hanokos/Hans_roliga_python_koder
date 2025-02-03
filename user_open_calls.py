import sys
import time
import tkinter as tk
from tkinter import scrolledtext
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

# Global Variables
driver = None
project_details = []

def open_browser():
    global driver

    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--kiosk")  # Fullscreen mode (locks browser)
    chrome_options.add_argument("--disable-new-tab-first-run")  # Prevents new tabs on first run
    chrome_options.add_argument("--disable-popup-blocking")  # Prevent pop-ups
    chrome_options.add_argument("--disable-infobars")  # Removes Chrome "info" bar
    chrome_options.add_argument("--disable-features=TabHoverCards")  # Disable tab preview
    chrome_options.add_experimental_option("excludeSwitches", ["disable-popup-blocking", "enable-automation"])
    chrome_options.add_experimental_option("detach", False)  # Prevent user from detaching the window
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # Start Chrome in locked mode
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Open the VR website
    driver.get("https://www.vr.se/english/applying-for-funding/calls-and-decisions.html?filters=callsOpen;&selectedSubject=all")

    # Force window on top
    root.attributes('-topmost', 1)  # Keep the button window on top

def extract_open_calls():
    global project_details

    if not driver:
        print("Error: Selenium driver is not running.")
        return

    # Wait for page to fully load
    time.sleep(3)

    # Extract page source
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find all valid project links
    links = soup.find_all("a", href=True)
    call_links = [link for link in links if link["href"].startswith("/english/applying-for-funding/calls/")]

    # Extract project details
    project_details = []
    for link in call_links:
        full_url = f"https://www.vr.se{link['href']}"
        title = link.get_text(strip=True)
        date_text = link.find_parent("div").find("p", class_="content__list__text__date").text.strip() if link.find_parent("div") else "No date"

        project_details.append({
            "Title": title,
            "Link": full_url,
            "Date": date_text
        })

    # Close browser (forcefully)
    driver.quit()

    # Hide the main window after loading calls
    root.withdraw()  # Hide the main window

    # Show results
    show_results_window()

def show_results_window():
    result_window = tk.Toplevel(root)
    result_window.title("Open Calls Results")
    result_window.geometry("600x400")
    result_window.attributes('-topmost', 1)  # Keep results window on top

    # Display count of open calls
    count_label = tk.Label(result_window, text=f"Found {len(project_details)} Open Calls", font=("Arial", 14, "bold"))
    count_label.pack(pady=10)

    # Scrollable text box
    result_text = scrolledtext.ScrolledText(result_window, width=70, height=15)
    result_text.pack(padx=10, pady=10)

    # Populate the list
    for project in project_details:
        result_text.insert(tk.END, f"Title: {project['Title']}\n")
        result_text.insert(tk.END, f"Link: {project['Link']}\n")
        result_text.insert(tk.END, f"Date: {project['Date']}\n")
        result_text.insert(tk.END, "-" * 50 + "\n")

    result_text.config(state=tk.DISABLED)

    # Add Quit button to close the application
    quit_button = tk.Button(result_window, text="Quit", command=root.quit, font=("Arial", 12), padx=10, pady=5)
    quit_button.pack(pady=20)

# Main GUI
root = tk.Tk()
root.title("VR Open Calls Scraper")
root.geometry("400x200")
root.attributes('-topmost', 1)  # Keep the button window on top

open_button = tk.Button(root, text="Open VR Website", command=open_browser, font=("Arial", 12), padx=10, pady=5)
open_button.pack(pady=10)

load_button = tk.Button(root, text="Load Open Calls", command=extract_open_calls, font=("Arial", 12), padx=10, pady=5)
load_button.pack(pady=10)

root.mainloop()

# to complicated to explain with little aount of text right now. but basically i can retrieve all open calls correctly and their links

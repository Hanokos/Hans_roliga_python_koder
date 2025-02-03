import sys
import time
import tkinter as tk
from tkinter import scrolledtext
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import InvalidSessionIdException
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import requests
import re
import threading

# Global Variables
driver = None
project_details = []
TARGET_URL = "https://www.vr.se/english/applying-for-funding/calls-and-decisions.html?filters=callsOpen;&selectedSubject=all"
monitor_running = True  # Flag to control the monitor thread

def open_browser():
    global driver

    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--kiosk")  # Fullscreen mode
    chrome_options.add_argument("--disable-new-tab-first-run")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-features=TabHoverCards")
    chrome_options.add_experimental_option("excludeSwitches", ["disable-popup-blocking", "enable-automation"])
    chrome_options.add_experimental_option("detach", False)
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # Start Chrome in locked mode
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Open the target URL
    driver.get(TARGET_URL)

    # Keep the main window on top
    root.attributes('-topmost', 1)
    
    # Start monitoring the URL in a separate daemon thread
    threading.Thread(target=monitor_url, daemon=True).start()

def monitor_url():
    global driver, monitor_running

    while monitor_running:
        time.sleep(0.2)  # Check frequently for instant reaction
        try:
            # Only proceed if driver is still valid
            if driver and driver.session_id:
                current_url = driver.current_url
                if current_url != TARGET_URL:
                    driver.get(TARGET_URL)  # Instantly reset the URL
                    time.sleep(0.1)  # Give it a tiny pause to reload
        except (InvalidSessionIdException, Exception) as e:
            # If the driver session is invalid or we get a connection error, stop the monitoring thread
            # (Suppress the error messages during shutdown.)
            break

def extract_open_calls():
    global project_details

    if not driver:
        print("Error: Selenium driver is not running.")
        return

    # Instead of a fixed sleep, we could wait briefly, but here we'll use a short sleep
    time.sleep(1)  # Allow the page to settle

    # Extract the page source
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find all valid project links
    links = soup.find_all("a", href=True)
    call_links = [link for link in links if link["href"].startswith("/english/applying-for-funding/calls/")]

    # Extract project details
    project_details = []
    for link in call_links:
        full_url = f"https://www.vr.se{link['href']}"
        title = link.get_text(strip=True)
        date_text = (link.find_parent("div")
                     .find("p", class_="content__list__text__date").text.strip()
                     if link.find_parent("div") else "No date")
        project_details.append({
            "Title": title,
            "Link": full_url,
            "Date": date_text
        })

    # Close the Selenium browser
    try:
        driver.quit()
    except Exception:
        pass

    # Stop the monitor thread
    stop_monitoring()

    # Show results
    show_results_window()

def extract_themes():
    themes = []
    for project in project_details:
        url = project['Link']
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        text_content = soup.get_text()
        match = re.search(r'Subject area:\s*(.*?)\s*Support form:', text_content)
        if match:
            subject_area = match.group(1).strip()
            themes.append(subject_area)
    show_themes_window(themes)

def show_themes_window(themes):
    theme_window = tk.Toplevel(root)
    theme_window.title("Project Themes")
    theme_window.geometry("600x400")
    theme_window.attributes('-topmost', 1)
    theme_window.protocol("WM_DELETE_WINDOW", quit_application)

    theme_label = tk.Label(theme_window, text=f"Found {len(themes)} Project Themes", font=("Arial", 14, "bold"))
    theme_label.pack(pady=10)

    theme_text = scrolledtext.ScrolledText(theme_window, width=70, height=15)
    theme_text.pack(padx=10, pady=10)
    for theme in themes:
        theme_text.insert(tk.END, f"Theme: {theme}\n")
        theme_text.insert(tk.END, "-" * 50 + "\n")
    theme_text.config(state=tk.DISABLED)

def show_results_window():
    root.withdraw()  # Hide the main window
    result_window = tk.Toplevel(root)
    result_window.title("Open Calls Results")
    result_window.geometry("600x400")
    result_window.attributes('-topmost', 1)
    result_window.protocol("WM_DELETE_WINDOW", quit_application)

    count_label = tk.Label(result_window, text=f"Found {len(project_details)} Open Calls", font=("Arial", 14, "bold"))
    count_label.pack(pady=10)

    result_text = scrolledtext.ScrolledText(result_window, width=70, height=15)
    result_text.pack(padx=10, pady=10)
    for project in project_details:
        result_text.insert(tk.END, f"Title: {project['Title']}\n")
        result_text.insert(tk.END, f"Link: {project['Link']}\n")
        result_text.insert(tk.END, f"Date: {project['Date']}\n")
        result_text.insert(tk.END, "-" * 50 + "\n")
    result_text.config(state=tk.DISABLED)

    open_diagram_button = tk.Button(result_window, text="Open Diagram", command=extract_themes, font=("Arial", 12), padx=10, pady=5)
    open_diagram_button.pack(pady=10)

    quit_button = tk.Button(result_window, text="Quit", command=quit_application, font=("Arial", 12), padx=10, pady=5)
    quit_button.pack(pady=10)

def stop_monitoring():
    global monitor_running
    monitor_running = False

def quit_application():
    # Stop monitoring and close the Selenium driver if it's still open
    stop_monitoring()
    try:
        if driver:
            driver.quit()
    except Exception:
        pass
    root.destroy()
    sys.exit()

# Main GUI
root = tk.Tk()
root.title("VR Open Calls Scraper")
root.geometry("400x200")
root.attributes('-topmost', 1)
root.protocol("WM_DELETE_WINDOW", quit_application)

open_button = tk.Button(root, text="Open VR Website", command=open_browser, font=("Arial", 12), padx=10, pady=5)
open_button.pack(pady=10)

load_button = tk.Button(root, text="Load Open Calls", command=extract_open_calls, font=("Arial", 12), padx=10, pady=5)
load_button.pack(pady=10)

quit_button = tk.Button(root, text="Quit", command=quit_application, font=("Arial", 12), padx=10, pady=5)
quit_button.pack(pady=10)

root.mainloop()

# TO complicated to explain how it works
# If you manage to make this code work on your PC, 
# It is worth noting when shutting the program down by either pressing quit or the X button the small pop-up windows take a little short while to make it close all windows down and end the process.

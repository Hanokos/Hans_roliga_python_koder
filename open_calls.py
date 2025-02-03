import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def fetch_open_calls():
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headless (without opening browser window)
    chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
    chrome_options.add_argument("--no-sandbox")  # Disable sandboxing for better compatibility
    chrome_options.add_argument("--disable-dev-shm-usage")  # Fix potential issue with limited shared memory
    chrome_options.add_argument("start-maximized")  # Maximize the window

    # Set up webdriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Open the website
    driver.get("https://www.vr.se/english/applying-for-funding/calls-and-decisions.html?filters=callsOpen;&selectedSubject=all")
    
    # Wait for the page to load
    time.sleep(3)

    # Keep clicking the "Show more" button until it disappears
    while True:
        try:
            # Try to find and click the "Show more" button
            show_more_button = driver.find_element(By.CLASS_NAME, "content_loadmore")
            show_more_button.click()
            print("Clicked 'Show more' button...")
            time.sleep(2)  # Wait for the content to load
        except:
            print("No more 'Show more' button found or failed to click.")
            break

    # After loading all content, extract the links
    print("Extracting links after all content is loaded...")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    links = soup.find_all("a", href=True)

    # Filter out the links that point to open calls (based on their structure)
    call_links = [link for link in links if link['href'].startswith('/english/applying-for-funding/calls/')]
    
    # Collect and display the project details
    project_details = []
    for link in call_links:
        full_url = f"https://www.vr.se{link['href']}"
        title = link.get_text(strip=True)
        
        # Extract the date (can be tricky depending on the exact structure, adjusting as needed)
        date_text = link.find_parent("div").find("p", class_="content__list__text__date").text.strip() if link.find_parent("div") else "No date"
        
        project_details.append({
            "Title": title,
            "Link": full_url,
            "Date": date_text
        })

    # Print the project details and count the open calls
    print(f"Found {len(project_details)} open calls:")
    for project in project_details:
        print(f"Title: {project['Title']}\nLink: {project['Link']}\nDate: {project['Date']}\n")

    # Close the browser
    driver.quit()

if __name__ == "__main__":
    fetch_open_calls()


# this cant press the "Show more open calls" button to find ALL open calls project right now.
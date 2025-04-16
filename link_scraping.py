from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import os
import argparse


def setup_chrome_driver():
    # Set up Chrome options for headful browsing
    chrome_options = Options()
    # Remove headless option to make it headful (visible browser)
    # chrome_options.add_argument("--headless")  # This is commented out for headful mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Initialize the Chrome driver with Service object
    chromedriver_path = r"C:\Users\Chris Joel\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

def save_page_html(driver, url, output_dir="html_output2"):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate a filename from the URL
    filename = url.replace("https://", "").replace("http://", "").replace("/", "_") + ".html"
    filepath = os.path.join(output_dir, filename)
    
    try:
        # Navigate to the URL
        driver.get(url)
        
        # Check for common captcha indicators
        captcha_indicators = [
            "captcha",
            "verify you are not a bot",
            "recaptcha",
            "human verification"
        ]
        
        page_source = driver.page_source.lower()
        if any(indicator in page_source for indicator in captcha_indicators):
            print(f"Captcha detected on {url}")
            print("Please solve the captcha in the browser window...")
            # Wait for user to solve captcha (manual intervention)
            input("Press Enter after solving the captcha...")
        
        # Wait 1 second for dynamic content to load
        time.sleep(1)
        
        # Get the fully rendered page source
        html_content = driver.page_source
        
        # Save to file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Saved HTML for {url} to {filepath}")
        
    except Exception as e:
        print(f"Error processing {url}: {str(e)}")

def process_links(links, output_dir="html_output2"):
    # Get list of existing files in existing_dir (html_output)
    
    # Setup the driver
    driver = setup_chrome_driver()
    
    try:
        # Process each link
        for link in links:
            print(f"Processing: {link}")
            save_page_html(driver, link, output_dir)
            
    finally:
        # Clean up: close the browser
        driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Save HTML pages from links.")
    parser.add_argument('--linkpath', type=str, required=True, help='Path to links JSON file')
    parser.add_argument('--HTMLsavepath', type=str, required=True, help='Path to save the HTML files')
    args = parser.parse_args()

    with open(args.linkpath, "r", encoding='utf8') as file:
        links_data = json.load(file)
    BASE_URL = "https://www.canlii.org"
    links_to_scrape = []
    
    for i, item in enumerate(links_data):
        # Construct the full URL
        full_url = BASE_URL + item["path"]
        links_to_scrape.append(full_url)

    # Run the script
    process_links(links_to_scrape, output_dir=args.HTMLsavepath)
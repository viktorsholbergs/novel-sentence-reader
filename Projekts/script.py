from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# You can adjust this if chromedriver is installed in a different location
CHROMEDRIVER_PATH = "/usr/bin/chromedriver"

# URL to scrape
url = "https://www.lightnovelworld.co/novel/lord-of-the-mysteries-275/chapter-1-16091324"

# Start Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")  # Show the browser window
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

try:
    driver.get(url)
    time.sleep(5)  # Wait for content to load (increase if necessary)

    # Extract the text inside the chapter container
    chapter_element = driver.find_element(By.ID, "chapter-container")
    chapter_text = chapter_element.text.strip()

    with open("chapter_text.txt", "w", encoding="utf-8") as f:
        f.write(chapter_text)
    print("[✓] Chapter text saved to 'chapter_text.txt'.")

    # Extract the href for the next chapter
    next_button = driver.find_element(By.CSS_SELECTOR, 'a.chnav.next')
    next_href = next_button.get_attribute("href")

    with open("next_chapter_url.txt", "w", encoding="utf-8") as f:
        f.write(next_href)
    print(f"[✓] Next chapter link saved to 'next_chapter_url.txt': {next_href}")

    # Optional: keep browser open until you press Enter
    input("Press Enter to close the browser...")

finally:
    driver.quit()

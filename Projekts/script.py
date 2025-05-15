from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import os

# Config
CHROMEDRIVER_PATH = "/usr/bin/chromedriver"
BASE_URL = "https://www.lightnovelworld.co"
START_URL = f"{BASE_URL}/novel/the-mirror-legacy-1685/chapter-1"

# Setup Chrome
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

# Create folder to save output
os.makedirs("chapters", exist_ok=True)

chapter_counter = 1
current_url = START_URL

try:
    while True:
        print(f"\n[→] Loading Chapter {chapter_counter}: {current_url}")
        driver.get(current_url)
        time.sleep(2)  # Adjust based on your connection

        try:
            # Extract chapter text
            chapter_element = driver.find_element(By.ID, "chapter-container")
            chapter_text = chapter_element.text.strip()

            # Save chapter text
            filename = f"chapters/chapter_{chapter_counter}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(chapter_text)
            print(f"[✓] Saved to {filename}")

            # Try to find the next link
            next_button = driver.find_element(By.CSS_SELECTOR, 'a.chnav.next')
            next_href = next_button.get_attribute("href")

            if not next_href:
                print("[✕] No href found in next button.")
                break

            # Prepare for next loop
            current_url = BASE_URL + next_href if next_href.startswith("/") else next_href
            chapter_counter += 1

        except NoSuchElementException:
            print("[✔] No next chapter link found. Done.")
            break

except Exception as e:
    print(f"[ERROR] {e}")

finally:
    driver.quit()
    print("\n[✓] All done.")

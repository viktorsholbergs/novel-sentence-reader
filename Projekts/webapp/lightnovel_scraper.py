import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

class LightNovelScraper:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.base_url = "https://www.lightnovelworld.co"

    def _get_novel_name(self, url):
        """Extracts and formats the novel name from the URL."""
        parts = url.split("/novel/")[1].split("/")
        name_slug = parts[0]
        name_parts = name_slug.split("-")
        if name_parts and name_parts[-1].isdigit():
            name_parts = name_parts[:-1]
        name = " ".join(name_parts).title()
        return name

    def scrape_from(self, start_url):
        novel_name = self._get_novel_name(start_url)
        folder_name = f"Projekts/webapp/novels/{novel_name}"
        os.makedirs(folder_name, exist_ok=True)

        current_url = start_url
        chapter_counter = 1

        print(f"\n[] Scraping novel: {novel_name}")
        print(f"[] Saving chapters in: {folder_name}\n")

        try:
            while True:
                print(f"[→] Chapter {chapter_counter}: {current_url}")
                self.driver.get(current_url)
                time.sleep(1)  # Adjust if needed

                # Extract chapter text
                chapter_element = self.driver.find_element(By.ID, "chapter-container")
                chapter_text = chapter_element.text.strip()

                # Save to file
                file_path = os.path.join(folder_name, f"chapter_{chapter_counter}.txt")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(chapter_text)
                print(f"[✓] Saved: {file_path}")

                # Try to find the next chapter link
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, 'a.chnav.next')
                    next_href = next_button.get_attribute("href")
                    if not next_href:
                        print("[✔] End of chapters.")
                        break
                    if next_href.startswith("/"):
                        current_url = self.base_url + next_href
                    else:
                        current_url = next_href
                    chapter_counter += 1
                except NoSuchElementException:
                    print("[✔] No next button found. Done.")
                    break

        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            self.driver.quit()
            print("\n[✓] Scraping complete.")


# Allow this file to run standalone for testing
if __name__ == "__main__":
    scraper = LightNovelScraper()
    scraper.scrape_from("https://www.lightnovelworld.co/novel/i-shall-be-everlasting-in-the-world-of-immortals-1683/chapter-1")

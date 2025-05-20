# Import built-in modules for file handling and time delays
import os
import time

# Import Selenium components for controlling the browser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service  # Required to start ChromeDriver
from selenium.webdriver.chrome.options import Options  # To set Chrome startup options
from selenium.webdriver.common.by import By  # For locating elements on the page
from selenium.common.exceptions import NoSuchElementException  # For handling missing elements

# Automatically handles downloading and setting up the right ChromeDriver
from webdriver_manager.chrome import ChromeDriverManager


# Define the main scraper class
class LightNovelScraper:
    def __init__(self):
        # Initialize Chrome browser options
        options = Options()
        options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)
        options.add_argument("--no-sandbox")  # Required for running as root or in some Linux configs
        options.add_argument("--disable-dev-shm-usage")  # Avoid shared memory issues
        options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration (not needed in headless)
        

        # Initialize ChromeDriver with options, downloaded and managed by webdriver-manager
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

        # Set the base URL of the site (used to join relative links)
        self.base_url = "https://www.lightnovelworld.co"

    # Helper function to extract and format the novel's title from the URL
    def _get_novel_name(self, url):
        # Split the URL to isolate the novel part
        parts = url.split("/novel/")[1].split("/")
        name_slug = parts[0]
        name_parts = name_slug.split("-")

        # Remove trailing chapter number if present (e.g., "title-1683")
        if name_parts and name_parts[-1].isdigit():
            name_parts = name_parts[:-1]

        # Convert slug to a nicely formatted title (e.g., "i-shall-be" → "I Shall Be")
        name = " ".join(name_parts).title()
        return name

    # Main function to start scraping from a given chapter URL
    def scrape_from(self, start_url):
        # Format the novel name from the URL
        novel_name = self._get_novel_name(start_url)

        # Build folder path where chapters will be saved
        folder_name = f"/novels/{novel_name}"

        # Create the folder if it doesn't exist
        os.makedirs(folder_name, exist_ok=True)

        # Start from the given URL
        current_url = start_url
        chapter_counter = 1  # Track chapter number

        # Inform the user what novel is being scraped
        print(f"\n[] Scraping novel: {novel_name}")
        print(f"[] Saving chapters in: {folder_name}\n")

        try:
            while True:  # Continue until no more chapters
                # Show which chapter is being scraped
                print(f"[→] Chapter {chapter_counter}: {current_url}")

                # Load the chapter webpage in the browser
                self.driver.get(current_url)
                time.sleep(1)  # Wait a bit for the page to load

                # Find the main text container by its HTML ID
                chapter_element = self.driver.find_element(By.ID, "chapter-container")

                # Get the chapter text content and strip extra whitespace
                chapter_text = chapter_element.text.strip()

                # Create file path to save the chapter
                file_path = os.path.join(folder_name, f"chapter_{chapter_counter}.txt")

                # Write the chapter content to a text file
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(chapter_text)
                print(f"[✓] Saved: {file_path}")

                try:
                    # Try to locate the "next chapter" button
                    next_button = self.driver.find_element(By.CSS_SELECTOR, 'a.chnav.next')

                    # Get the next chapter's URL
                    next_href = next_button.get_attribute("href")

                    # If no URL is found, exit the loop
                    if not next_href:
                        print("[✔] End of chapters.")
                        break

                    # Update current URL, handle relative or absolute URLs
                    if next_href.startswith("/"):
                        current_url = self.base_url + next_href
                    else:
                        current_url = next_href

                    # Increment chapter number
                    chapter_counter += 1

                except NoSuchElementException:
                    # If the "next" button is missing, exit loop
                    print("[✔] No next button found. Done.")
                    break

        except Exception as e:
            # Catch and print any errors that occur during scraping
            print(f"[ERROR] {e}")

        finally:
            # Always close the browser when done
            self.driver.quit()
            print("\n[✓] Scraping complete.")


# Run the scraper as a standalone script (for testing)
if __name__ == "__main__":
    # Create a scraper instance
    scraper = LightNovelScraper()

    # Start scraping from Chapter 1 of a specific novel
    scraper.scrape_from("https://www.lightnovelworld.co/novel/i-shall-be-everlasting-in-the-world-of-immortals-1683/chapter-1")

import json
import os
import re
import time
import shutil
from datetime import datetime, timedelta
from RPA.Browser.Selenium import Selenium
from RPA.Tables import Tables
from RPA.Robocorp.WorkItems import WorkItems
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import Config
from date_extractor import DateExtractor

import hashlib


class NewsScraper:
    def __init__(self):
        self.browser = Selenium()
        self.tables = Tables()
        self.work_items = WorkItems()
        self.config = Config()

        self.search_phrase = self.config.search_phrase
        self.news_category = self.config.news_category
        self.months = self.config.months
        self.date_limit = datetime.today() - timedelta(days=self.months * 30)

        self.scraps_directory = self.create_scraps_directory()
        self.date_extractor = DateExtractor()
        self.downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
        self.directory_name = ""

    def create_scraps_directory(self):
        today = datetime.today().strftime('%Y-%m-%d')
        directory_name = f"{today}_{self.search_phrase.replace(' ', '_')}"
        directory_path = os.path.join(os.path.dirname(__file__), 'scraps', directory_name)
        os.makedirs(directory_path, exist_ok=True)
        return directory_path

    def find_element_dynamically(self, selectors):
        for selector in selectors:
            try:
                print(f"Trying selector: {selector}")
                element = self.browser.find_element(selector)
                print(f"Element found using selector: {selector}")
                return element
            except Exception:
                continue
        raise Exception(f"None of the selectors worked: {selectors}")

    def find_element_dynamically_in_element(self, parent, selectors):
        for selector in selectors:
            try:
                element = parent.find_element(selector)
                return element
            except Exception:
                continue
        raise Exception(f"None of the selectors worked within the element: {selectors}")


    def filter_by_category(self):
        if self.news_category:
            category_selectors = [
                f'css:[data-category="{self.news_category}"]', 
                f'css:.category-{self.news_category}', 
                f'css:a[href*="{self.news_category}"]'
            ]
            category_element = self.find_element_dynamically(category_selectors)
            
            WebDriverWait(self.browser.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, category_element))
            )
            
            self.browser.click_element(category_element)

    def sort_results_by_date(self):
        time.sleep(10)
        try:
            self.browser.select_from_list_by_value('id:search-sort-option', 'date')
            print("Sorted results by date.")
        except Exception as e:
            print(f"Failed to sort results by date: {e}")

        time.sleep(10)

    def close_registration_popup(self):
        try:
            self.browser.execute_javascript("""
                const popupCloseButton = document.querySelector('button.close-button');
                if (popupCloseButton) {
                    popupCloseButton.click();
                }
            """)
            print("Registration popup closed.")
        except Exception as e:
            print(f"Failed to close registration popup: {e}")

    def get_latest_downloaded_file(self):
        files = [os.path.join(self.downloads_folder, f) for f in os.listdir(self.downloads_folder)]
        latest_file = max(files, key=os.path.getctime)
        return latest_file

    def save_image(self, image_url):
        # Extração da extensão do arquivo a partir do URL, se disponível
        image_extension = image_url.split('.')[-1] if '.' in image_url.split('/')[-1] else 'jpg'
        image_hash = hashlib.md5(image_url.encode('utf-8')).hexdigest()
        image_filename = f"{image_hash}.{image_extension}"
        file_path = os.path.join(self.scraps_directory, image_filename)
        
        # JavaScript para criar o link de download
        self.browser.execute_javascript(f"""
            var link = document.createElement('a');            
            link.href = '{image_url}';            
            link.download = '{image_filename}';            
            document.body.appendChild(link);            
            link.click();            
            document.body.removeChild(link);
        """)

        time.sleep(5)

        try:
            latest_file = self.get_latest_downloaded_file()
            shutil.move(latest_file, file_path)
            print(f"Image moved to {file_path}")
        except Exception as e:
            print(f"Error moving downloaded file: {e}")


    def extract_news_dates(self, news_items):

        last_date = None
        news_data = []

        for item in news_items:
            print(item)

            try:
                title_element = item.find_element(By.CSS_SELECTOR, 'h3.gc__title')
                title = title_element.text if title_element else "N/A"

                # date and description are in the same element
                date_description_element = item.find_element(By.CSS_SELECTOR, 'div.gc__excerpt p')
                date_description_text = date_description_element.text.strip() if date_description_element else "N/A"

                # Extract date and description
                date_text, description = self.extract_date_and_description(date_description_text)
                date_text = item.find_element(By.CSS_SELECTOR, 'span.screen-reader-text').text
                date_text = date_text.replace("Published On","").strip()
                date_text = date_text.replace("Last update","").strip()
                print(f"DATA PORRA {date_text}")

                print(f"Extracted date and description: {date_text} |||| {description}")

                try:
                    if "ago" in date_text:
                        date_text = self.convert_relative_date(date_text)
                    try:
                        parsed_date = datetime.strptime(date_text, '%d %B %Y')
                    except ValueError:
                        parsed_date = datetime.strptime(date_text, '%d %b %Y')
                    date_text = parsed_date.strftime('%d/%m/%Y')
                except ValueError as ve:
                    parsed_date = None
                    print(f"Error parsing date '{date_text}': {ve}")

                # Image element
                image_element = item.find_element(By.CSS_SELECTOR, 'div.responsive-image img')
                image_url = image_element.get_attribute('src') if image_element else "N/A"
                image_filename = os.path.basename(image_url) if image_url else "N/A"

                news_data.append({
                    'title': title,
                    'date': date_text,
                    'description': description,
                    'image_filename': image_filename,
                    'count_search_phrase': title.lower().count(self.search_phrase.lower()) + description.lower().count(self.search_phrase.lower()),
                    'contains_money': bool(re.search(r'\$\d+(?:,\d{3})*(?:\.\d{2})?|dollars|USD', title + description))
                })

                if parsed_date and (last_date is None or parsed_date > last_date):
                    last_date = parsed_date

                if image_url and image_url != "N/A":
                    time.sleep(5)
                    self.save_image(image_url)
                    time.sleep(5)
            except Exception as e:
                print(f"Error extracting news item: {e}")
                continue

        return last_date, news_data

    def extract_date_and_description(self, text):
            parts = text.split(' ... ')
            if len(parts) >= 2:
                return parts[0].strip(), ' '.join(parts[1:]).strip()
            return text, ""

    def convert_relative_date(self, relative_date_str):
        now = datetime.now()
        if 'days ago' in relative_date_str:
            days = int(relative_date_str.split()[0])
            return (now - timedelta(days=days)).strftime('%d %B %Y')
        elif 'hrs ago' in relative_date_str:
            hours = int(relative_date_str.split()[0])
            return (now - timedelta(hours=hours)).strftime('%d %B %Y')
        elif 'hours ago' in relative_date_str:
            hours = int(relative_date_str.split()[0])
            return (now - timedelta(hours=hours)).strftime('%d %B %Y')
        return relative_date_str

    def navigate_and_extract(self):
        last_date = None
        all_news_data = []

        time.sleep(5)
        self.sort_results_by_date()
        time.sleep(5)

        while True:
            print("Looking for news items on the page...")
            news_items = self.browser.find_elements('css:article.gc--list')
            
            print(f"Found {len(news_items)} news items on the current page.")

            last_date, news_data = self.extract_news_dates(news_items)
            all_news_data.extend(news_data)

            if last_date is None or last_date < self.date_limit:
                break

            try:
                show_more_button = self.browser.find_element(By.CSS_SELECTOR, 'button.show-more-button')
                if show_more_button.is_enabled():
                    self.browser.click_element(show_more_button)
                    time.sleep(5)
                else:
                    break
            except Exception as e:
                print(f"Could not find or click the 'Show more' button: {e}")
                break

        return all_news_data

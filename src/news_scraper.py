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
from openpyxl import Workbook
from config import Config
from date_extractor import DateExtractor

from selenium.webdriver.chrome.options import Options

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

        self.images_directory = self.create_images_directory()
        self.date_extractor = DateExtractor()

    def create_images_directory(self):
        today = datetime.today().strftime('%Y-%m-%d')
        directory_name = f"{today}_{self.search_phrase.replace(' ', '_')}"
        directory_path = os.path.join(os.path.dirname(__file__), 'images', directory_name)
        os.makedirs(directory_path, exist_ok=True)
        return directory_path

    def open_site(self, url):
        chrome_options = Options()
        chrome_prefs = {
            "profile.default_content_settings.popups": 0,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "profile.content_settings.exceptions.automatic_downloads.*.setting": 1,  # Allow automatic downloads
            "download.default_directory": os.path.join(os.path.dirname(__file__), 'downloads')
        }
        chrome_options.add_experimental_option("prefs", chrome_prefs)
        #chrome_options.add_argument("--headless")
        #chrome_options.add_argument("--disable-gpu")
        #chrome_options.add_argument("--window-size=1920,1080")
        
        self.browser.open_available_browser(url, options=chrome_options)

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

    def close_cookies_banner(self):
        try:
            self.browser.execute_javascript("""
                const cookiesButtons = document.querySelectorAll('button, div[role="button"], span[role="button"]');
                for (const button of cookiesButtons) {
                    if (button.textContent.toLowerCase().includes('accept') || button.textContent.toLowerCase().includes('agree')) {
                        button.click();
                        break;
                    }
                }
            """)
            print("Cookies banner closed.")
        except Exception as e:
            print(f"Failed to close cookies banner: {e}")

    def search_news(self):
        time.sleep(10)
        self.close_cookies_banner()
        time.sleep(10)

        button_found = self.browser.execute_javascript("""
            const logs = [];
            logs.push('Searching for SVGs...');
            const svgs = document.querySelectorAll('svg');
            logs.push('SVGs found: ' + svgs.length);
            
            for (const svg of svgs) {
                const attributes = svg.attributes;
                let isSearchIcon = false;
                for (const attr of attributes) {
                    logs.push('SVG attribute: ' + attr.name + ', ' + attr.value);
                    if (attr.value.includes('search')) {
                        isSearchIcon = true;
                        break;
                    }
                }
                if (isSearchIcon) {
                    let button = svg.closest('button, a, div[role="button"], span[role="button"]');
                    if (button) {
                        logs.push('Found search icon, clicking button...');
                        const event = new MouseEvent('click', {
                            view: window,
                            bubbles: true,
                            cancelable: true
                        });
                        button.dispatchEvent(event);
                        return {logs: logs, clicked: true};
                    }
                }
            }
            
            logs.push('Searching for button with data-testid...');
            let button = document.querySelector('button[data-testid="search-button"]');
            if (button) {
                logs.push('Found search button, attempting to click...');
                const event = new MouseEvent('click', {
                    view: window,
                    bubbles: true,
                    cancelable: true
                });
                button.dispatchEvent(event);

                if (button.offsetParent !== null && !button.disabled) {
                    logs.push('Button is visible and enabled, clicked successfully.');
                    return {logs: logs, clicked: true};
                } else {
                    logs.push('Button is not visible or enabled.');
                }
            } else {
                logs.push('Search button not found.');
            }

            return {logs: logs, clicked: false};
        """)

        for log in button_found['logs']:
            print(log)

        if not button_found['clicked']:
            raise Exception("Search button not found or not interactable")
        
        time.sleep(10)

        search_field = self.browser.execute_javascript("""
            function findSearchField() {
                const inputs = document.querySelectorAll('input');
                for (const input of inputs) {
                    if (input.placeholder && input.placeholder.toLowerCase().includes('search')) {
                        return input;
                    }
                    if (input.title && input.title.toLowerCase().includes('search')) {
                        return input;
                    }
                }
                return null;
            }
            return findSearchField();
        """)

        if search_field is None:
            raise Exception("Search field not found")

        time.sleep(10)
        self.browser.input_text(search_field, self.search_phrase)
        time.sleep(10)
        self.browser.press_keys(search_field, 'ENTER')
        time.sleep(10)

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

    def save_image(self, image_url, file_path):
        file_url = f"file:///{file_path.replace(os.sep, '/')}"
        self.browser.execute_javascript(f"""
        var link = document.createElement('a');            
        link.href = '{image_url}';            
        link.download = '{file_url}';            
        document.body.appendChild(link);            
        link.click();            
        document.body.removeChild(link);
        """)

        downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
        downloaded_file = os.path.join(downloads_folder, os.path.basename(image_url))
        time.sleep(5)

        if os.path.exists(downloaded_file):
            shutil.move(downloaded_file, file_path)
            print(f"Image moved to {file_path}")
        else:
            print(f"Downloaded file not found: {downloaded_file}")


    """
    def extract_news(self):
        news_data = []
        time.sleep(20)
        self.close_registration_popup()
        time.sleep(10)

        news_items = self.browser.find_elements('css:div[data-testid="liverpool-article"]')
        extracted_dates = self.date_extractor.extract_news_dates(news_items)

        for idx, item in enumerate(news_items):
            try:
                title_element = item.find_element('css selector', 'h2[data-testid="card-headline"]')
                title = title_element.text if title_element else "N/A"

                #date = extracted_dates[idx].strftime('%d/%m/%Y') if idx < len(extracted_dates) and extracted_dates[idx] else "N/A"
                dates = self.date_extractor.extract_news_dates([item])
                date = dates[0] if dates else "N/A"

                description_element = item.find_element('css selector', 'p[data-testid="card-description"]')
                description = description_element.text if description_element else "N/A"

                image_element = item.find_element('css selector', 'div[data-testid="card-media"] img')
                image_url = image_element.get_attribute('src') if image_element else "N/A"
                image_filename = os.path.basename(image_url) if image_url else "N/A"

                search_phrase_lower = self.search_phrase.lower()
                count_search_phrase = title.lower().count(search_phrase_lower) + description.lower().count(search_phrase_lower)

                news_data.append({
                    'title': title,
                    'date': date,
                    'description': description,
                    'image_filename': image_filename,
                    'count_search_phrase': count_search_phrase,
                    'contains_money': bool(re.search(r'\$\d+(?:,\d{3})*(?:\.\d{2})?|dollars|USD', title + description))
                })

                if image_url and image_url != "N/A":
                    time.sleep(5)
                    self.save_image(image_url, os.path.join(self.images_directory, image_filename))
                    time.sleep(5)
            except Exception as e:
                print(f"Error extracting news item: {e}")
                continue

        for x in news_data:
            print(x)

        return news_data
    
    """
    def extract_news_dates(self, news_items):
        last_date = None
        news_data = []

        for item in news_items:
            try:
                title_element = item.find_element(By.CSS_SELECTOR, 'h2[data-testid="card-headline"]')
                title = title_element.text if title_element else "N/A"

                date_element = item.find_element(By.CSS_SELECTOR, 'span[data-testid="card-metadata-lastupdated"]')
                date_text = date_element.text.strip() if date_element else "N/A"
                if date_text == "":
                    date_text = date_element.get_attribute('innerText').strip()

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

                description_element = item.find_element(By.CSS_SELECTOR, 'p[data-testid="card-description"]')
                description = description_element.text if description_element else "N/A"

                image_element = item.find_element(By.CSS_SELECTOR, 'div[data-testid="card-media"] img')
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
                    self.save_image(image_url, os.path.join(self.images_directory, image_filename))
                    time.sleep(5)
            except Exception as e:
                print(f"Error extracting news item: {e}")
                continue

        return last_date, news_data

    def convert_relative_date(self, relative_date_str):
        now = datetime.now()
        if 'days ago' in relative_date_str:
            days = int(relative_date_str.split()[0])
            return (now - timedelta(days=days)).strftime('%d %B %Y')
        elif 'hrs ago' in relative_date_str:
            hours = int(relative_date_str.split()[0])
            return (now - timedelta(hours=hours)).strftime('%d %B %Y')
        return relative_date_str

    def navigate_and_extract(self):
        last_date = None
        page = 1
        all_news_data = []

        time.sleep(20)
        self.close_registration_popup()
        time.sleep(10)

        while True:
            news_items = self.browser.find_elements('css:div[data-testid="liverpool-article"]')
            last_date, news_data = self.extract_news_dates(news_items)
            all_news_data.extend(news_data)
            
            if last_date is None or last_date < self.date_limit:
                break

            print(f"Moving to page {page+1}")
            try:
                next_page_button = self.browser.find_element('css:button[data-testid="pagination-next-button"]')
                if next_page_button and next_page_button.is_enabled():
                    self.browser.click_element(next_page_button)
                    time.sleep(5)
                    page += 1
                else:
                    break
            except Exception as e:
                print(f"Could not find or click the next page button: {e}")
                break

        return all_news_data


    def save_to_excel(self, news_data):
        if isinstance(news_data, list) and all(isinstance(item, dict) for item in news_data):
            all_keys = set().union(*(d.keys() for d in news_data))
            for item in news_data:
                for key in all_keys:
                    if key not in item:
                        item[key] = "N/A"

            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "News Data"
            headers = list(all_keys)
            sheet.append(headers)

            for item in news_data:
                row = [item.get(key, "N/A") for key in headers]
                sheet.append(row)

            excel_path = os.path.join(os.path.dirname(__file__), 'news_data.xlsx')
            workbook.save(excel_path)
            print(f"Data saved to {excel_path}")
        else:
            raise TypeError("Not a valid input format")

    def close(self):
        self.browser.close_all_browsers()

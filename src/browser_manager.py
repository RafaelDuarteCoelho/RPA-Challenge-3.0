from RPA.Browser.Selenium import Selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
import time

class BrowserManager:
    def __init__(self):
        self.browser = Selenium()

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
        
        self.browser.open_available_browser(url, options=chrome_options)
        return self.browser

    def close(self):
        self.browser.close_all_browsers()

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
from RPA.Browser.Selenium import Selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class BrowserManager:
    def __init__(self):
        self.browser = Selenium()

    def open_site(self, url):
        self.browser.open_available_browser(url)

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
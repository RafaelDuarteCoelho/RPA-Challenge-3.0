from RPA.Browser.Selenium import Selenium
from selenium.webdriver.chrome.options import Options
import os

class BrowserManager:
    def __init__(self):
        # Initialize the Selenium browser instance
        self.browser = Selenium()

    def open_site(self, url):
        """
        Opens the browser and navigates to the specified URL with custom Chrome options.

        Args:
            url (str): The URL of the website to open.
        
        Returns:
            Selenium: The configured Selenium browser instance.
        """
        # Chrome browser settings
        chrome_options = Options()
        chrome_prefs = {
            "profile.default_content_settings.popups": 0,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "profile.content_settings.exceptions.automatic_downloads.*.setting": 1,  # Allow automatic downloads
            "download.default_directory": os.path.join(os.path.dirname(__file__), 'downloads')  # Download directory
        }
        chrome_options.add_experimental_option("prefs", chrome_prefs)
        # chrome_options.add_argument("--headless")  # Option to run the browser in headless mode (no GUI)
        
        # Open the browser with the configured options
        self.browser.open_available_browser(url, options=chrome_options)
        return self.browser

    def close(self):
        """
        Closes all browsers opened by Selenium.
        """
        self.browser.close_all_browsers()

    def close_cookies_banner(self):
        """
        Automatically closes the cookies banner on the website, if possible.
        """
        try:
            # Executes a JavaScript script to click the accept cookies button
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
        """
        Attempts to find an element on the page using a provided list of selectors.

        Args:
            selectors (list): List of CSS selectors to try to find the element.
        
        Returns:
            WebElement: The found element.
        
        Raises:
            Exception: If none of the selectors find the element.
        """
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
        """
        Attempts to find an element within a parent element using a provided list of selectors.

        Args:
            parent (WebElement): The parent element where the search will be performed.
            selectors (list): List of CSS selectors to try to find the element.
        
        Returns:
            WebElement: The found element.
        
        Raises:
            Exception: If none of the selectors find the element within the parent element.
        """
        for selector in selectors:
            try:
                element = parent.find_element(selector)
                return element
            except Exception:
                continue
        raise Exception(f"None of the selectors worked within the element: {selectors}")

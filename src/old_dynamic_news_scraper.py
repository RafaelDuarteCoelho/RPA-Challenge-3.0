import os
from RPA.Browser.Selenium import Selenium
import time
import json
import random

class DynamicNewsScraper:
    def __init__(self, config_path=None):
        self.browser = Selenium()
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        self.config_path = config_path
        self.settings = self.load_config()

    def load_config(self):
        with open(self.config_path, 'r') as file:
            return json.load(file)

    def open_site(self, url):
        self.browser.open_available_browser(url)
        time.sleep(3)  # Wait for the site to load

    def scrape_news(self):
        news_data = []
        for article_selector in self.settings['article_selectors']:
            articles = self.browser.find_elements(article_selector)
            for article in articles:
                data = {}
                for key, value in self.settings['data_selectors'].items():
                    try:
                        data[key] = self.browser.get_text(value, parent=article)
                    except Exception as e:
                        print(f"Failed to get {key}: {str(e)}")
                news_data.append(data)
        return news_data

    def close(self):
        self.browser.close_all_browsers()

# Example usage
if __name__ == "__main__":
    scraper = DynamicNewsScraper()
    scraper.open_site('https://news.yahoo.com/')
    news = scraper.scrape_news()
    print(news)
    scraper.close()
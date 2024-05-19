import json
import re
import os
from datetime import datetime, timedelta
from RPA.Browser.Selenium import Selenium
from RPA.Tables import Tables
from RPA.Robocorp.WorkItems import WorkItems
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from news_scraper import NewsScraper

import time



def main():
    scraper = NewsScraper()
    #scraper.open_site('https://www.aljazeera.com/')
    scraper.open_site('https://www.bbc.com/')
    #scraper.open_site('https://www.nytimes.com/')
    #scraper.open_site('https://www.washingtonpost.com/')
    scraper.search_news()
    #scraper.sort_results_by_date()
    news_data = scraper.extract_news()
    #scraper.save_to_excel(news_data)
    #scraper.close()

if __name__ == "__main__":
    main()
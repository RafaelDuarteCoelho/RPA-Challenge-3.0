from news_scraper import NewsScraper
from file_manager import FileManager
from browser_manager import BrowserManager
from searcher_engine import search_news


def main():
    scraper = NewsScraper()
    browser = BrowserManager()

    scraper.browser = browser.open_site('https://www.aljazeera.com/')
    search_news(scraper.browser, scraper.search_phrase)

    #scraper.open_site('https://www.bbc.com/')
    #scraper.open_site('https://www.nytimes.com/')

    #scraper.search_news()

    news_data = scraper.navigate_and_extract()
    FileManager.save_to_excel(news_data, scraper.scraps_directory, scraper.directory_name)
    #scraper.close()
    browser.close()

if __name__ == "__main__":
    main()
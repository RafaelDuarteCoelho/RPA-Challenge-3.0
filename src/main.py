from news_scraper import NewsScraper
from file_manager import FileManager


def main():
    scraper = NewsScraper()
    scraper.open_site('https://www.bbc.com/')
    #scraper.open_site('https://www.aljazeera.com/')
    #scraper.open_site('https://www.nytimes.com/')
    #scraper.open_site('https://www.washingtonpost.com/')
    scraper.search_news()
    news_data = scraper.navigate_and_extract()
    FileManager.save_to_excel(news_data)
    scraper.close()

if __name__ == "__main__":
    main()
import time
from datetime import datetime
from RPA.Browser.Selenium import Selenium

class DateExtractorTest:
    def __init__(self):
        self.browser = Selenium()
        self.search_phrase = "german"
        print("INICIADO TESTE")

    def open_site(self, url):
        self.browser.open_available_browser(url)


    def extract_news_dates(self):
        news_items = self.browser.find_elements('css:div[data-testid="liverpool-article"]')

        for item in news_items:
            try:
                # Extraindo o texto do elemento da data
                date_element = item.find_element('css selector', 'span[class^="sc-"][data-testid="card-metadata-lastupdated"]')
                if date_element:
                    # Adicionando log para HTML do elemento
                    date_element_html = date_element.get_attribute('outerHTML')
                    print(f"Found date element HTML: {date_element_html}")

                    # Extraindo o texto do elemento
                    date_text = date_element.text.strip()
                    print(f"Found date element with text: '{date_text}'")
                    if date_text == "":
                        # Extraindo o texto do elemento usando innerText
                        date_text = date_element.get_attribute('innerText').strip()

                    # Tentando fazer o parse da data
                    try:
                        parsed_date = datetime.strptime(date_text, '%d %B %Y')
                    except ValueError as ve:
                        parsed_date = None
                        print(f"Error parsing date '{date_text}': {ve}")

                    print(f"Extracted date: {date_text} -> Parsed date: {parsed_date}")
                else:
                    print("Date element not found or not visible")
            except Exception as e:
                print(f"Error extracting date: {e}")
                continue

    def close(self):
        self.browser.close_all_browsers()

# Execução do script de teste
test = DateExtractorTest()
test.open_site("https://www.bbc.com/search?q=german&edgeauth=eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJrZXkiOiAiZmFzdGx5LXVyaS10b2tlbi0xIiwiZXhwIjogMTcxNTk3OTMzOCwibmJmIjogMTcxNTk3ODk3OCwicmVxdWVzdHVyaSI6ICIlMkZzZWFyY2glM0ZxJTNEZ2VybWFuIn0.6PeMgyhKY6yy9zZD8X-E-JzzSehHvBcPUt3GXj3u-i0")

test.extract_news_dates()
test.close()
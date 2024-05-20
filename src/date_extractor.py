import re
from datetime import datetime, timedelta

class DateExtractor:
    def parse_relative_date(self, date_text):
        print(date_text)

        """Convert relative dates like '6 days ago' to absolute dates."""
        today = datetime.today()
        match = re.match(r'(\d+)\s+(hour|hours|hr|hrs|day|days|week|weeks|month|months|year|years)\s+ago', date_text)
        if match:
            amount, unit = match.groups()
            amount = int(amount)
            if unit.startswith('hour'):
                return today - timedelta(hours=amount)
            if unit.startswith('hr'):
                return today - timedelta(hours=amount)
            elif unit.startswith('day'):
                return today - timedelta(days=amount)
            elif unit.startswith('week'):
                return today - timedelta(weeks=amount)
            elif unit.startswith('month'):
                return today - timedelta(days=amount * 30)  # Rough approximation
            elif unit.startswith('year'):
                return today - timedelta(days=amount * 365)  # Rough approximation
        return None

    def extract_news_dates(self, news_items):
        extracted_dates = []
        for item in news_items:
            try:
                date_element = item.find_element('css selector', 'span[class^="sc-"][data-testid="card-metadata-lastupdated"]')
                if date_element:
                    date_element_html = date_element.get_attribute('outerHTML')
                    print(f"Found date element HTML: {date_element_html}")

                    date_text = date_element.text.strip()
                    print(f"Found date element with text: '{date_text}'")
                    if date_text == "":
                        date_text = date_element.get_attribute('innerText').strip()

                    parsed_date = None
                    if re.match(r'\d+ \w+ \d{4}', date_text):
                        try:
                            parsed_date = datetime.strptime(date_text, '%d %B %Y')
                        except ValueError as ve:
                            print(f"Error parsing date '{date_text}': {ve}")
                    else:
                        parsed_date = self.parse_relative_date(date_text)

                    if parsed_date:
                        formatted_date = parsed_date.strftime('%d/%m/%Y')
                        print(f"Extracted date: {date_text} -> Parsed date: {formatted_date}")
                        extracted_dates.append(formatted_date)
                    else:
                        print(f"Failed to parse date: {date_text}")
                        extracted_dates.append("N/A")
                else:
                    print("Date element not found or not visible")
                    extracted_dates.append("N/A")
            except Exception as e:
                print(f"Error extracting date: {e}")
                extracted_dates.append("N/A")
        return extracted_dates
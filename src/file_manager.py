from openpyxl import Workbook
import os

class FileManager:
    @staticmethod
    def save_to_excel(news_data, scraps_directory, directory_name):
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
            
            excel_path = os.path.join(scraps_directory, 'news_data.xlsx')
            #excel_path = os.path.join(os.path.dirname(__file__), 'news_data.xlsx')
            workbook.save(excel_path)
            print(f"Data saved to {excel_path}")
        else:
            raise TypeError("Not a valid input format")

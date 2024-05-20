from openpyxl import Workbook
import os

class FileManager:
    @staticmethod
    def save_to_excel(news_data, scraps_directory):
        """
        Saves news data to an Excel file.

        Args:
            news_data (list): List of dictionaries containing the news data.
            scraps_directory (str): Directory where the Excel file will be saved.
        
        Raises:
            TypeError: If the input format is not a list of dictionaries.
        """
        # Check if news_data is a list of dictionaries
        if isinstance(news_data, list) and all(isinstance(item, dict) for item in news_data):
            # Collect all keys from the dictionaries to ensure all columns are present
            all_keys = set().union(*(d.keys() for d in news_data))
            # Add the key "N/A" for items that do not have certain keys
            for item in news_data:
                for key in all_keys:
                    if key not in item:
                        item[key] = "N/A"
            
            # Create a new workbook and select the first sheet
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "News Data"
            
            # Add headers (keys) in the first row
            headers = list(all_keys)
            sheet.append(headers)
            
            # Add news data in subsequent rows
            for item in news_data:
                row = [item.get(key, "N/A") for key in headers]
                sheet.append(row)
            
            # Define the full path for the Excel file
            excel_path = os.path.join(scraps_directory, 'news_data.xlsx')
            #excel_path = os.path.join(os.path.dirname(__file__), 'news_data.xlsx')  # Alternative to define the path
            
            # Save the Excel file at the specified path
            workbook.save(excel_path)
            print(f"Data saved to {excel_path}")
        else:
            raise TypeError("Not a valid input format")

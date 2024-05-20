import os
import json
from RPA.Robocorp.WorkItems import WorkItems

class Config:
    def __init__(self):
        """
        Initializes the Config class. If the environment variables 'RC_WORKSPACE_ID' and 'RC_API_SECRET' 
        are set, it retrieves the work item data from Robocorp Control Room. Otherwise, it loads the configuration 
        from a local config.json file.
        """
        if "RC_WORKSPACE_ID" in os.environ and "RC_API_SECRET" in os.environ:
            self.workitems = WorkItems()
            self.workitems.get_input_work_item()
            self.data = self.workitems.get_work_item_data()
        else:
            # Local development mode with default data
            self.data = self.load_config()

    def load_config(self):
        """
        Loads configuration data from a local config.json file.

        Returns:
            dict: Configuration data from config.json.
        
        Raises:
            FileNotFoundError: If config.json is not found in the script's directory.
        """
        print("WARNING! Workitem not found. The parameters will be the default on config.json")
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        with open(config_path) as config_file:
            return json.load(config_file)

    @property
    def search_phrase(self):
        """
        Retrieves the search phrase from the configuration data.

        Returns:
            str: The search phrase.
        """
        return self.data.get("search_phrase", "example search")

    @property
    def news_category(self):
        """
        Retrieves the news category from the configuration data.

        Returns:
            str: The news category.
        """
        return self.data.get("news_category", "technology")

    @property
    def months(self):
        """
        Retrieves the number of months from the configuration data.

        Returns:
            int: The number of months.
        """
        return int(self.data.get("months", 1))
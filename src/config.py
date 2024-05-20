import os
import json
from RPA.Robocorp.WorkItems import WorkItems

class Config:
    def __init__(self):
        if "RC_WORKSPACE_ID" in os.environ and "RC_API_SECRET" in os.environ:
            self.workitems = WorkItems()
            self.workitems.get_input_work_item()
            self.data = self.workitems.get_work_item_data()
        else:
            # Modo de desenvolvimento local com dados fictícios
            self.data = self.load_config()

    def load_config(self):
        print("WARNING! Workitem not found. The parameters will be the default on config.json")
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        with open(config_path) as config_file:
            return json.load(config_file)

    @property
    def search_phrase(self):
        return self.data.get("search_phrase", "example search")

    @property
    def news_category(self):
        return self.data.get("news_category", "technology")

    @property
    def months(self):
        return int(self.data.get("months", 1))

# Config.py Test
config = Config()
print(config.search_phrase)
print(config.news_category)
print(config.months)
import os
import json
from RPA.Robocorp.WorkItems import WorkItems

class Config:
    def __init__(self):
        # Verifique se as variáveis de ambiente estão definidas
        if "RC_WORKSPACE_ID" in os.environ and "RC_API_SECRET" in os.environ:
            self.workitems = WorkItems()
            self.workitems.get_input_work_item()
            self.data = self.workitems.get_work_item_data()
        else:
            # Modo de desenvolvimento local com dados fictícios
            self.data = {
                "search_phrase": "example search",
                "news_category": "technology",
                "months": 1
            }

    @property
    def search_phrase(self):
        return self.data.get("search_phrase")

    @property
    def news_category(self):
        return self.data.get("news_category")

    @property
    def months(self):
        return int(self.data.get("months", 0))

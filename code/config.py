from boards import boards
import re
import os
from datetime import date

current_date = date.today()
year = current_date.year
   

class DataProject:
    def __init__(self) -> None:
        super().__init__()
        self.project_id = os.environ['PROJECT_ID']
        self.key = os.environ['KEY']
        self.service_account = os.environ['SERVICE_ACOUNT']
        self.version = os.environ['VERSION']
        self.api_url = os.environ['API_URL']
        self.data_set = os.environ['DATA_SET']
        self.limit_data = 100
        # self.table_name_old_projects = ['old_projects', 'old_projects_consultants']
        # self.table_name_current_projects = ['current_projects', 'current_projects_consultants']
        # self.table_name_consultants_allocation = ["data_consultants", "data_allocation"]

class DataMonday(DataProject):
    def __init__(self):
        super().__init__()
        self.boards = boards(self.project_id, self.key, self.version, self.api_url)
        self.old_projects = self.old_projects()
        self.current_projects = self.current_projects()
        self.consultants = self.consultants()
        
    def show_board(self):
        return self.boards
    
    def old_projects(self):
        board_id = None
        for board in self.boards:
            if re.search(r'old', board['name'].lower()) and not re.search(r'sub', board['name'].lower()):
                board_id = board['id']
        return board_id
    
    def current_projects(self):
        board_id = None
        for board in self.boards:
            if re.search(r'opt', board['name'].lower()) and not re.search(r'sub', board['name'].lower()):
                board_id = board['id']
        return board_id
    
    def consultants(self):
        board_id = {}
        allocation_current_year = None
        allocation_previous_year = []
        for board in self.boards:
            if re.search(r'consultor', board['name'].lower()) and not re.search(r'sub', board['name'].lower()):
                if re.search(f"{year}", board["name"].lower()):
                    allocation_current_year = board['id']
                else:
                    allocation_previous_year.append(board['id'])
            board_id = {
                'current_year': allocation_current_year,
                'previous_year': allocation_previous_year
            }
        return board_id

class ConfigData(DataMonday):
    def __init__(self):
        super().__init__()
        self.boards_id = {
            "old_projects": self.old_projects,
            "current_projects": self.current_projects,
            "consultant_allocation": self.consultants
        }
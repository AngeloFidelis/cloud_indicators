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
        self.limit_data = 500
        self.regex_old_board = os.environ['REGEX_OLD_BOARD']
        self.regex_actual_board = os.environ['REGEX_CURRENT_BOARD']
        self.regex_consultant = os.environ['REGEX_CONSULTANT']
        self.regex_not_in_board = os.environ['REGEX_NOT_IN_BOARD']
        self.spreadsheet_id = os.environ['SAMPLE_SPREADSHEET_ID']
        self.range_name = os.environ['SAMPLE_RANGE_NAME']

class DataMonday(DataProject):
    def __init__(self):
        super().__init__()
        self.boards = boards(self.project_id, self.key, self.version, self.api_url)
        self.consultants = self.consultants_function()
        self.old_projects = self.old_projects_function()
        self.current_projects= self.current_projects_function()
        
        
        
    def show_board(self):
        return self.boards
    
    def old_projects_function(self):
        board_id = None
        for board in self.boards:
            if re.search(f'{self.regex_old_board}', board['name'].lower()) and not re.search(f'{self.regex_not_in_board}', board['name'].lower()):
                board_id = board['id']
        return board_id
    
    def current_projects_function(self):
        board_id = None
        for board in self.boards:
            if re.search(f'{self.regex_actual_board}', board['name'].lower()) and not re.search(f'{self.regex_not_in_board}', board['name'].lower()):
                board_id = board['id']
        return board_id
    
    def consultants_function(self):
        board_id = {}
        allocation_current_year = None
        allocation_previous_year = []
        for board in self.boards:
            if re.search(f'{self.regex_consultant}', board['name'].lower()) and not re.search(f'{self.regex_not_in_board}', board['name'].lower()):
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
            "old_projects": self.old_projects_function(),
            "current_projects": self.current_projects,
            "consultant_allocation": self.consultants
        }
class ConfigData:
    def __init__(self) -> None:
        self.project_id = 'lookerstudylab'
        self.key = 'api_key'
        self.version = 'latest'
        self.api_url = 'https://api.monday.com/v2'
        self.data_set = 'cloud_indicators'
        self.table_name_old_projects = ['old_projects', 'old_projects_consultants']
        self.table_name_actual_projects = ['actual_projects', 'actual_projects_consultants']
        self.table_name_consultants_allocation = ["data_consultants", "data_allocation"]
        self.board = {
            "old_projects": 6695876611,
            "actual_projects": 6519449128,
            "allocation_consultant": 7262468157
        }
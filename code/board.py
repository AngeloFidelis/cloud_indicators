import requests
from secret import secrets
from config import ConfigData

config_data = ConfigData()
request_key = secrets(config_data.project_id)
api_key = request_key(config_data.key[0], 'latest')

headers = {"Authorization" : api_key}

query = """
query {
    boards {
        id, 
        name 
    }
}
"""

data = {'query': query}
response = requests.post(url=config_data.api_url, json=data, headers=headers)

boards = response.json()['data']['boards']

for board in boards:
    print(board)

from secret import secrets
import requests

def boards(project_id, key, version,api_url):
    request_key = secrets(project_id) #Chama a função 'secrets' passando o 'project_id' da configuração.
    api_key = request_key(key, version) # Obtém o nome do 'secret' para a api_key

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
    response = requests.post(url=api_url, json=data, headers=headers)

    boards = response.json()['data']['boards']
    
    return boards
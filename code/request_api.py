import requests
import time
from secret import secrets
from config import ConfigData

begin = time.time() # Registra o horário de início da execução do script
config_data = ConfigData() # Cria uma instância da classe 'ConfigData' que carrega dados de configuração
request_key = secrets(config_data.project_id) #Chama a função 'secrets' passando o 'project_id' da configuração.

api_key = request_key('api_key', 'latest') # Obtém o nome do 'secret' para a api_key

def request_api(board):
  headers = {"Authorization" : api_key} # Define o cabeçalho da requisição HTTP, incluindo o campo "Authorization" onde a chave da API é usada para autenticar
  query = """ 
  query GetBoardItems($boardId: [ID!]){  
    boards(ids: $boardId) {  
      columns {
        id
        title
        type
      }
      items_page(limit: 300) {  
        cursor
        items {  
          id  
          name
          column_values {  
            id  
            text
            column {
              id
              title
            }
          }  
          subitems {
              id
              name
              column_values {
                  id
                  text
                  column {
                      id
                      title
                  }
              }
          }
        }  
      }  
    }  
  }
  """

  variables = { # Define as variáveis que serão enviadas na requisição, neste caso, um dicionário com o ID do quadro
    "boardId": [board]
  }
  data = {'query': query, 'variables': variables} # Cria o payload para a requisição POST, que consiste em um dicionário contendo a 'query' e as 'variables' 

  response_data = requests.post(url=config_data.api_url, json=data, headers=headers) # Envia uma requisição HTTP POST para a URL da API
  end = time.time() # Registra o horário após a conclusão do script
  print(f'- {round(end - begin, 2)} segundos para a extração dos dados') # Calcula a diferença entre o tempo de início e o tempo de término em segundos
  return response_data
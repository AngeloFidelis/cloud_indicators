import requests
from secret import secrets
from config import ConfigData

config_data = ConfigData() # Cria uma instância da classe 'ConfigData' que carrega dados de configuração
request_key = secrets(config_data.project_id) #Chama a função 'secrets' passando o 'project_id' da configuração.
api_key = request_key('api_key', 'latest') # Obtém o nome do 'secret' para a api_key
headers = {"Authorization" : api_key}
# data_limit = config_data.limit_data
data_limit = 250

def get_items_board(board,limit):
    query = """ 
    query GetBoardItems($boardId: [ID!], $limit: Int){  
        boards(ids: $boardId) {  
        columns {
            id
            title
            type
        }
        items_page(limit: $limit) {  
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
        "boardId": [board],
        "limit": limit
    }
    data = {'query': query, 'variables': variables}
    return data

def next_page(board, cursor,limit):
    query = """ 
    query FetchNextItems($cursor: String!, $limit: Int!) {
        next_items_page(limit: $limit, cursor: $cursor) {
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

    """

    variables = { # Define as variáveis que serão enviadas na requisição, neste caso, um dicionário com o ID do quadro
        "cursor": cursor,
        "limit": limit
    }
    data = {'query': query, 'variables': variables}
    return data

def request(board):
    data = get_items_board(board,data_limit)#pega todos os itens
    response_data = requests.post(url=config_data.api_url, json=data, headers=headers).json()
    return response_data

def request_projects(board):
    data = get_items_board(board,data_limit)#pega todos os itens
    response_data = requests.post(url=config_data.api_url, json=data, headers=headers).json()#transforma esses dados em json
    data_len = response_data["data"]["boards"][0]["items_page"]["items"].__len__()
    cursor = response_data['data']['boards'][0]["items_page"]['cursor']
    
    schema_projects, schema_subitems = create_schema(response_data)
    schema_subitems = ['id_project', 'name'] + schema_subitems
    
    print(data_len)
    # quando o cursor for nulo, quer dizer que não há mais dados para paginar, fazendo o loop terminar
    if cursor is not None:
        all_data = create_pagination(response_data,cursor,board)
        return all_data, schema_projects, schema_subitems
    else:
        return response_data["data"]["boards"][0]["items_page"]["items"], schema_projects, schema_subitems
    # return response_data,schema_projects
    
def request_consultants(board):
    all_consultants_data = [] #Variável que será usando para fazer um append nos dados de consultores de todos os boards
    for key, values in board.items():
        if key == 'current_year':
            response_data = request(values)
            schema_consultants, schema_subitems = create_schema(response_data)
            schema_subitems = ['employee_id', 'allocation'] + schema_subitems
            
            data_len = response_data["data"]["boards"][0]["items_page"]["items"].__len__()
            cursor = response_data['data']['boards'][0]["items_page"]['cursor']
            if cursor is not None:
                all_data = create_pagination(response_data,cursor,board)
                for item in all_data: #impede que os dados sejam armazenados como uma lista dentro de outra lista
                    all_consultants_data.append(item)
            else:
                data = response_data["data"]["boards"][0]["items_page"]["items"]
                for item in data: #impede que os dados sejam armazenados como uma lista dentro de outra lista
                    all_consultants_data.append(item)
        else:
            for value in values:
                response_data = request(value)
                cursor = response_data['data']['boards'][0]["items_page"]['cursor']
                if cursor is not None:
                    all_data = create_pagination(response_data,cursor,board)
                    for item in all_data: #impede que os dados sejam armazenados como uma lista dentro de outra lista
                        all_consultants_data.append(item)
                else:
                    data = response_data["data"]["boards"][0]["items_page"]["items"]
                    for item in data: #impede que os dados sejam armazenados como uma lista dentro de outra lista
                        all_consultants_data.append(item)
    return all_consultants_data, schema_consultants, schema_subitems
    
def create_schema(response_data):
    schema_subitems = []
    main_schema = [
        items["title"]
        for items
        in response_data['data']['boards'][0]['columns']
    ]
    subitems = [
        items['subitems']
        for items
        in response_data['data']['boards'][0]['items_page']['items']
    ]
    
    #interators
    subitems_iterators = subitems.__iter__()
    
    while True:
        try:
            validate_data_is_empty = subitems_iterators.__next__()
            # valida se o subitems é ou não vazio
            if validate_data_is_empty.__len__() != 0:
                columns_name = [
                    item['column']['title']
                    for item
                    in validate_data_is_empty[0]['column_values']
                ]
                schema_subitems = columns_name
                #após a primeira ocorrencia, sair do loop
                break
        except:
            break
    return main_schema, schema_subitems

def create_pagination(response_data,cursor,board):
    pagination = []
    pagination.append(response_data["data"]["boards"][0]["items_page"]["items"])
    while cursor is not None:
        data_pagination = next_page(board, cursor,data_limit)
        response_data_pagination = requests.post(url=config_data.api_url, json=data_pagination, headers=headers).json()
        pagination.append(response_data_pagination['data']['next_items_page']['items'])
        cursor = response_data_pagination['data']['next_items_page']['cursor']
        data_len = response_data_pagination["data"]["next_items_page"]["items"].__len__()
        print(data_len)
    #Selecione o item de cada items dentro da paginação de cada item para cada items
    all_data = [
        item
        for items
        in pagination
        for item
        in items
    ]
    
    return all_data
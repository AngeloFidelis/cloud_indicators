import pandas as pd
from random import randint
from request_api import request_api
import time
import pandas_gbq as pdb
# import os
from config import ConfigData
import re

PATH = './'

project_list = []
subitems_list = []

# remover as variáveis de ambiente
config_data = ConfigData()
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.environ["SECURITY_CREDENTIALS"]
    
def split_data(items, opt, client, project_name, id_project, project_list, subitems_list, current_row_items_list, current_row_subitems_list, current_subitems_values_list):
    for items_values in items['column_values']:
        current_row_items_list.append(items_values['text'])
    
    for subitems in items["subitems"]:
        subitem_values = []
        current_row_subitems_list.append(subitems['name'])
        for subitems_values in subitems['column_values']:
            subitem_values.append(subitems_values['text'])
        current_subitems_values_list.append([id_project] + [subitems['name']] + subitem_values)
    
    current_row_subitems_string = ', '.join(map(str, current_row_subitems_list))
    current_project = [id_project] + [opt] + [client] +[project_name] + current_row_items_list[1:]
    project_list.append(current_project)
    if current_subitems_values_list.__len__() != 0:
        subitems_list.append(current_subitems_values_list)

#Primeira função a ser chamada
# Ajeitar isso aqui depois 
def extract_data_api(data,project_list,subitems_list):
    for items in data["data"]["boards"][0]["items_page"]['items']:
        try:
            opt = items["name"][0:8] #Cria uma variável com a OPT do projeto
            client = items['name'].split(' - ')[1] #cria uma variável para o nome do cliente
            project_name = items['name'].split(' - ')[2] #Cria uma variável com o nome do projeto
            id_project = ''.join([opt.replace("-",''), str(randint(100000,999999))]) # Cria um id para o projeto com base na OPT            
            current_row_items_list = []
            current_row_subitems_list = []
            current_subitems_values_list = []
            
            #divide a lista com dados em uma lista para os projetos e outra lista para os subelementos
            split_data(
                items, 
                opt, 
                client, 
                project_name, 
                id_project, 
                project_list,
                subitems_list,
                current_row_items_list, 
                current_row_subitems_list,
                current_subitems_values_list
            )
            
        except IndexError:
            #esse error se dar por causa de atividades internas dentro do dataset
            opt, client, project_name, id_project = "interno", 'AvenueCode', items['name'], str(randint(100000,999999))
            current_row_items_list = []
            current_row_subitems_list = []
            current_subitems_values_list = []
            
            #divide a lista com dados em uma lista para os projetos e outra lista para os subelementos
            split_data(
                items, 
                opt, 
                client, 
                project_name, 
                id_project, 
                project_list,
                subitems_list,
                current_row_items_list, 
                current_row_subitems_list,
                current_subitems_values_list
            )

def create_dataset(project_list,subitems_list,schema_project,schema_subitems):
    #subitems_list é uma lista que contém outra lista
    #Para acessar a lista interna, vamos utilizar o seguinte código
    subitems_list = [
      items for subitems in subitems_list for items in subitems
    ]
    
    df_project = pd.DataFrame(project_list, columns=schema_project)
    df_subitems = pd.DataFrame(subitems_list, columns=schema_subitems)
    
    return [df_project, df_subitems]
    
def rename_coluns_dataset(df_project,df_subitems):
    replace_coluns_name_project = dict(
        zip(
            [col for col in df_project.columns], #usa o nome antigo das colunas como chave do objeto
            [col.lower().replace(" ","_") for col in df_project.columns] #usa o nome dome das colunas como valor
        )
    )
    df_project = df_project.rename(columns=replace_coluns_name_project)
    
    replace_coluns_name_subitems = dict(
        zip(
            [col for col in df_subitems.columns], #usa o nome antigo das colunas como chave do objeto
            [col.lower().replace(" ","_").replace("-_","") for col in df_subitems.columns] #usa o nome dome das colunas como valor
        )
    )
    df_subitems = df_subitems.rename(columns=replace_coluns_name_subitems)
    
    df_project = df_project.rename(columns={'us$_monthly_consumption': 'us_monthly_consumption'})
    df_project = df_project.rename(columns={'client': 'customer'})
    
    df_subitems = df_subitems.rename(columns={'consultor': 'consultant'})
    df_subitems = df_subitems.rename(columns={'name': 'role'})

    
    return df_project,df_subitems

def formula_data_null (df_project, df_subitems): #a api não consegue retornar valores de colunas de formula. Então, repetirei a formúla dentro do código
    
    ## ------------------------------ Formulas para calcular as horas e o custo ------------------------------
    # hours = Total_horas_trabalhadas * 8 (8 horas de trabalho por dia) / 100 * alocação no projeto
    # cost = Custo_por_hora_de_cada_consultor * Horas_totais
    df_subitems['hours'] = df_subitems.apply(
        lambda df: round(pd.to_numeric(df['working_days'], errors='coerce') * 8 / 100 * pd.to_numeric(df["allocation"], errors="coerce"), 2),
        axis=1
    )
    df_subitems['cost'] = pd.to_numeric(df_subitems['cost_per_hour']) * df_subitems['hours']
    df_subitems["role"] = df_subitems["role"].apply(lambda x: x.split(" - ")[0])
    
    ## ------------------------------ Salvar valores como 'working_days', 'cronograma', 'hours' e 'cost' na tabela 'df_project' ------------------------------
    # Foi feito uma concatenação no 'working_days' dentro da tabela 'df_project'
    # Foi feito uma concatenação no 'cronograma' dentro da tabela 'df_project'
    # Foi feito uma média agregada em 'hours' dentro da tabela 'df_project'
    # Foi feito uma soma agregada em 'cost' dentro da tabela 'df_project'
    
    for i, row_project in df_project.iterrows():
        matching_subitems = df_subitems[df_subitems['id_project'] == row_project['id_project']] #trazer dados do row_project que for igual a df_subitens
        if not matching_subitems.empty:
            # working_days = ', '.join(matching_subitems['working_days'].dropna())
            working_days = pd.to_numeric(matching_subitems['working_days']).dropna().max()
            cronograma = ', '.join([cron for cron in matching_subitems['cronograma'] if cron])
            hours = matching_subitems['hours'].dropna().max() #pegar o valor maximo de horas
            # hours = round(matching_subitems['hours'].dropna().mean(), 2) #pegar a media
            cost = matching_subitems['cost'].dropna().sum()
            
            #o 'at' vai selecionar apenas as linhas cujos ids do df_project correspondam aos ids do df_subitems
            df_project.at[i, 'working_days'] = working_days if working_days else None
            df_project.at[i, 'cronograma'] = cronograma.split(',')[0] if cronograma else None
            df_project.at[i, 'hours'] = hours if hours else '0'
            df_project.at[i, 'cost'] = cost if cost else '0'    
    
    ##  ------------------------------ Formula para calcular a margem ------------------------------
    # Lucro = Receita total - custos
    # Margem = Lucro / Receita * 100
    df_project['margin'] = df_project.apply(
        lambda df: (
            pd.to_numeric(df['revenue'], errors='coerce') - pd.to_numeric(df['cost'], errors='coerce')) / pd.to_numeric(df['revenue'].replace("0",'1'), errors='coerce'
        ),
        axis=1
    )
    
    df_subitems = df_subitems.drop("dependência", axis=1)
    
    return df_subitems, df_project

def split_cronograma(df_project, df_subitems):
    # Split cronograma in df_project
    df_project[['start', 'end']] = df_project['cronograma'].str.split(' - ', expand=True) if df_project['cronograma'] is not None else None  #Divide a coluna 'cronograma' em duas colunas 'start' e 'end' usando o delimitador ' - '.
                                                                                           #O argumento expand=True garante que o resultado seja dividido nas duas colunas distintas.
    df_project = df_project.drop('cronograma', axis=1) #Remove a coluna original 'cronograma' do DataFrame.
    cols = df_project.columns.tolist() #Transforma os nomes das colunas do DataFrame em uma lista.
    insert_at = cols.index('contract_type') + 1  #Encontra a posição da coluna 'status' no DataFrame e define a posição logo após 'status'.
    cols = cols[:insert_at] + ['start', 'end'] + cols[insert_at:-2] #Pega todas as colunas até a posição 'insert_at', insere 'start' e 'end', e adiciona o restante das colunas até as duas últimas.
                                                                    #As duas últimas são as colunas 'start' e 'end', e por isso são removidas
    df_project = df_project[cols] #Reordena o DataFrame com as colunas na nova ordem definida pela lista 'cols'.
    # Split cronograma in df_subitems
    df_subitems[['schedule_start', 'schedule_end']] = df_subitems['cronograma'].str.split(' - ', expand=True)
    df_subitems = df_subitems.drop('cronograma', axis=1)
    cols = df_subitems.columns.tolist()
    insert_at = cols.index('consultant') + 1
    cols = cols[:insert_at] + ['schedule_start', 'schedule_end'] + cols[insert_at:-2]
    df_subitems = df_subitems[cols]
    
    #return dos datasets
    return df_project, df_subitems

def format_data(df_project, df_subitems):  
    # ------------------------------ converter valores numericos para float e datetime e tratar valores nulos ------------------------------
    df_project["hours"] = pd.to_numeric(df_project["hours"], errors='coerce').fillna(0)
    df_project["revenue"] = pd.to_numeric(df_project["revenue"], errors='coerce').fillna(0)
    df_project["cost"] = pd.to_numeric(df_project["cost"], errors='coerce').fillna(0)
    df_project["cost"] = df_project["cost"].apply(lambda x: round(x,2))
    df_project["margin"] = pd.to_numeric(df_project["margin"], errors='coerce').fillna(0)
    df_project["margin"] = df_project["margin"].apply(lambda x: round(x,4))
    
    df_project["start"] = pd.to_datetime(df_project["start"], errors='coerce', format="%Y-%m-%d")
    df_project["end"] = pd.to_datetime(df_project["end"], errors='coerce', format="%Y-%m-%d")
    df_project["working_days"] = pd.to_numeric(df_project["working_days"], errors='coerce').fillna(0)

    df_subitems["allocation"] = pd.to_numeric(df_subitems["allocation"], errors='coerce').fillna(0)
    df_subitems["working_days"] = pd.to_numeric(df_subitems["working_days"], errors='coerce').fillna(0)
    df_subitems["hours"] = pd.to_numeric(df_subitems["hours"], errors='coerce').fillna(0)
    df_subitems["cost_per_hour"] = pd.to_numeric(df_subitems["cost_per_hour"], errors='coerce').fillna(0)
    df_subitems["cost"] = pd.to_numeric(df_subitems["cost"], errors='coerce').fillna(0)
    df_subitems["schedule_start"] = pd.to_datetime(df_subitems["schedule_start"], errors='coerce', format="%Y-%m-%d")
    df_subitems["schedule_end"] = pd.to_datetime(df_subitems["schedule_end"], errors='coerce', format="%Y-%m-%d")

    
    # ------------------------------ tratar valores do tipo 'object' ------------------------------
    colunas_object_project = df_project.select_dtypes(include='object').columns
    colunas_object_subitems = df_subitems.select_dtypes(include='object').columns
    
    for coluns in colunas_object_project:
        df_project[coluns] = df_project[coluns].apply(
            lambda x: str(x) if x not in [None, '', ' '] else 'N/A'
        )
    for coluns in colunas_object_subitems:
        df_subitems[coluns] = df_subitems[coluns].apply(
            lambda x: str(x) if x not in [None, '', ' '] else 'N/A'
        )

def load_data(df_project, df_subitems):
    df_project.to_csv(f"projects.csv", index=False)
    df_subitems.to_csv(f"subitems.csv", index=False)

def projects_opt():
    try:
        begin = time.time()
        data = request_api(config_data.board["actual_projects"]).json()
        schema_project = ['id_project', 'opt', 'client'] + [
            'project_name' if schema['title'] == 'Name' else schema['title']
            for schema in data["data"]["boards"][0]["columns"]
            if not re.search(r".*subelementos.*", schema['title'].lower())
        ]
        schema_subitems = ['id_project', 'name', 'Consultor', 'Cronograma', 'Billable', 'Allocation', 'Working Days', 'Hours', 'Cost per Hour', 'Cost', 'Dependência']

        extract_data_api(data,project_list,subitems_list)
        df_project, df_subitems = create_dataset(project_list,subitems_list, schema_project,schema_subitems)
        df_project,df_subitems = rename_coluns_dataset(df_project, df_subitems)
        df_subitems, df_project = formula_data_null(df_project, df_subitems)
        df_project, df_subitems = split_cronograma(df_project, df_subitems)
        format_data(df_project, df_subitems)
        load_data(df_project, df_subitems)
        return f"Tempo de execução do programa: {round(time.time() - begin, 2)} segundos"
    except Exception as e:
        raise Exception(f"Erro em projects_opt: {e}")
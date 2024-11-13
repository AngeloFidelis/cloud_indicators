import pandas as pd
from random import randint
from request_api import request_api
import time
import pandas_gbq as pdb
import os
from config import ConfigData
import re

# https://www.w3schools.com/python/python_regex.asp

PATH = './'

consultants_list = []
subitems_consultants_list = []
config_data = ConfigData()

def extract_data_api(data, consultants_list,subitems_consultants_list):
    for items in data["data"]["boards"][0]["items_page"]['items']:
        try:
            consultant = items['name']
            id_consultant = None
            release_date = []
            release = None
            current_consultant_values = []
            current_consultant_allocations = []
            current_allocations_consultant_values = []
            
            for items_values in items['column_values']:
                column_title = items_values['column']['title'].lower()
                if re.search(r".*id.*", column_title):
                    id_consultant = items_values['text']
                else:
                    current_consultant_values.append(items_values['text'])
            if id_consultant is None:
                raise ValueError("ID do consultor não encontrado!")
            
            #criar a logica de free_after aqui
            for subitems in items["subitems"]:
                subitem_values = []
                current_consultant_allocations.append(subitems['name'])
                for subitems_values in subitems['column_values']:
                    if subitems_values["column"]["title"] == 'Release Date':
                        # release_date.append(subitems_values['text']) #cria uma lista com as release date
                        if subitems_values['text'] != '':
                            release_date.append(subitems_values['text'])
                    subitem_values.append(subitems_values['text'])
                current_allocations_consultant_values.append([id_consultant] + [subitems['name']] + subitem_values)
                release = max(release_date)
            consultants_list.append([id_consultant, consultant] + current_consultant_values[1:2] + [release] + current_consultant_values[3:])
    
            if current_allocations_consultant_values.__len__() != 0:
                subitems_consultants_list.append(current_allocations_consultant_values)
   
        except:
            ...

def create_dataset(consultants_list, schema_consultants,subitems_consultants_list, schema_subitems_consultants):

    df_consultants = pd.DataFrame(consultants_list, columns=schema_consultants)
    #subitems_consultants_list é uma lista que contém outra lista
    #Para acessar a lista interna, vamos utilizar o seguinte código
    subitems_consultants_list = [
        items 
        for subitems in subitems_consultants_list 
        for items in subitems
    ]

    df_allocation = pd.DataFrame(subitems_consultants_list, columns=schema_subitems_consultants)
    
    return df_consultants, df_allocation

# função que vai definir a partir de quando o consultor vai estár disponivel
def rename_coluns_dataset(df_consultants,df_allocation):
    
    replace_coluns_name_consultants = dict(
        zip(
            [col for col in df_consultants.columns], #usa o nome antigo das colunas como chave do objeto
            [col.lower().replace(" - ","_").replace(" ","_").replace("-","_") for col in df_consultants.columns] #usa o nome dome das colunas como valor
        )
    )
    df_consultants = df_consultants.rename(columns=replace_coluns_name_consultants)
    df_consultants = df_consultants.rename(columns={"total_us$_cost":"total_us_cost"})
    
    replace_coluns_name_allocation = dict(
        zip(
            [col for col in df_allocation.columns], #usa o nome antigo das colunas como chave do objeto
            [col.lower().replace(" ","_").replace("-_","") for col in df_allocation.columns] #usa o nome dome das colunas como valor
        )
    )
    df_allocation = df_allocation.rename(columns=replace_coluns_name_allocation)
    df_allocation = df_allocation.rename(columns={"us$_cost":"us_cost"})
    
    return df_consultants,df_allocation
   
def modify_type_column(df_consultants,df_allocation):
    ...
    #Date
    columns_date_consultants = ["free_after", "ac_start", "ac_termination"]
    columns_date_allocation = ["start_date", "release_date"]
    df_consultants[columns_date_consultants] = df_consultants[columns_date_consultants].apply(pd.to_datetime)
    df_allocation[columns_date_allocation] = df_allocation[columns_date_allocation].apply(pd.to_datetime)
    
    #Date
    columns_number_consultants = [
        "total_us_cost", "24_q1_cost", "24_q2_cost", "24_q3_cost", "24_q4_cost", "presales_allocation", "24_09_hours", "24_10_hours", "24_11_hours", "24_12_hours"
    ]
    columns_number_allocation = ["alocation", "days", "hour_cost", "us_cost"]
    df_consultants[columns_number_consultants] = df_consultants[columns_number_consultants].apply(pd.to_numeric).fillna(0)
    df_allocation[columns_number_allocation] = df_allocation[columns_number_allocation].apply(pd.to_numeric).fillna(0)
    
    colunas_object_consultants = df_consultants.select_dtypes(include='object').columns
    colunas_object_allocation = df_allocation.select_dtypes(include='object').columns
    
    for coluns in colunas_object_consultants:
        df_consultants[coluns] = df_consultants[coluns].apply(
            lambda x: str(x) if x not in [None, '', ' '] else 'N/A'
        )
    for coluns in colunas_object_allocation:
        df_allocation[coluns] = df_allocation[coluns].apply(
            lambda x: str(x) if x not in [None, '', ' '] else 'N/A'
        )

def load_data(df_consultants,df_allocation):
    df_consultants.to_csv(f"{PATH}/test3.csv", index=False)
    df_allocation.to_csv(f"{PATH}/test4.csv", index=False)
    
    # path_table_consultants = ".".join([config_data.data_set, config_data.table_name_consultants_allocation[0]])
    # path_table_allocation = ".".join([config_data.data_set, config_data.table_name_consultants_allocation[1]])

    # pdb.to_gbq(df_consultants, path_table_consultants, if_exists='replace')
    # pdb.to_gbq(df_subitems, path_table_subitems, if_exists='replace')

def consultor_allocation():
    try:
        begin = time.time()
        data = request_api(config_data.board["allocation_consultant"]).json()
        
        schema_consultants = ["id_employee"] + [
            column['title']
            for column in data['data']['boards'][0]['columns']
            if not re.search(r".*id.*", column['title'].lower()) and column['title'] != 'Subelementos'
        ]   
        
        schema_subitems_consultants = ['id_consultant','allocation','Status', 'Start Date', 'Release Date', 'Alocation', 'Days', 'Hour Cost', 'US$ Cost']
        
        extract_data_api(data, consultants_list,subitems_consultants_list)
        df_consultants, df_allocation = create_dataset(consultants_list, schema_consultants,subitems_consultants_list, schema_subitems_consultants)
        df_consultants,df_allocation = rename_coluns_dataset(df_consultants,df_allocation)
        modify_type_column(df_consultants,df_allocation)
        load_data(df_consultants,df_allocation)
        print(df_consultants)
        return f"Tempo de execução do programa: {round(time.time() - begin, 2)} segundos"
    except Exception as e:
        raise Exception(f"Erro: {e}")
from config import ConfigData
from request_api import request_consultants
import re
import pandas as pd

config_data = ConfigData()

all_data = []
consultants_list = []
subitems_consultants_list = []

def extract_data_api(data, consultants_list,subitems_consultants_list):
    for items in data:
        consultant = items['name']
        id_consultant = None
        release_date = []
        release = None
        all_data_consultants = []
        all_data_allocation_by_consultants = []
        
        for items_values in items['column_values']:
            column_title = items_values['column']['title'].lower()
            if re.search(r".*id.*", column_title):
                id_consultant = items_values['text']
            else:
                all_data_consultants.append(items_values['text'])
        if id_consultant is None:
            raise ValueError("ID do consultor não encontrado!")
        
        #criar a logica de free_after aqui
        for subitems in items["subitems"]:
            subitem_values = []
            for subitems_values in subitems['column_values']:
                if subitems_values["column"]["title"] == 'Release Date':
                    # release_date.append(subitems_values['text']) #cria uma lista com as release date
                    if subitems_values['text'] != '':
                        release_date.append(subitems_values['text'])
                subitem_values.append(subitems_values['text'])
            all_data_allocation_by_consultants.append([id_consultant] + [subitems['name']] + subitem_values)
            if release_date.__len__() != 0:
                release = max(release_date)
            else:
                release = None
        consultants_list.append([id_consultant, consultant] + all_data_consultants[1:2] + [release] + all_data_consultants[3:])

        if all_data_allocation_by_consultants.__len__() != 0:
            subitems_consultants_list.append(all_data_allocation_by_consultants)

def create_dataset(consultants_list, new_schema_projects,subitems_consultants_list, schema_subitems_consultants):
    df_consultants = pd.DataFrame(consultants_list, columns=new_schema_projects)
    
    subitems_consultants_list = [
        items 
        for subitems in subitems_consultants_list 
        for items in subitems
    ]
    df_allocation = pd.DataFrame(subitems_consultants_list, columns=schema_subitems_consultants)
    
    return df_consultants, df_allocation

def define_area_consultants(df_consultants, df_area_consultants):
    new_dataframe = df_consultants.merge(df_area_consultants[['employee_id','Area']], how='left', on='employee_id')
    new_schema = ['employee_id'] + ['Name'] + ['Roles'] + ['Area'] + [col for col in new_dataframe.columns if col not in ['Name', 'employee_id', 'Area', 'Roles']]
    new_dataframe = new_dataframe[new_schema]
    return new_dataframe

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
    # Modificar o tipo das colunas do dataframe consultants
    columns_cost_projects = df_consultants.filter(regex='cost').columns
    columns_hours_projects = df_consultants.filter(regex='hours').columns
    columns_date_consultants = ["free_after", "ac_start", "ac_termination"]
    columns_object_consultants = df_consultants.select_dtypes(include='object').columns
    
    for coluns in columns_cost_projects:
        df_consultants[coluns] = pd.to_numeric(df_consultants[coluns], errors='coerce').fillna(0)
    for coluns in columns_hours_projects:
        df_consultants[coluns] = pd.to_numeric(df_consultants[coluns], errors='coerce').fillna(0)
    for coluns in columns_date_consultants:
        df_consultants[coluns] = pd.to_datetime(df_consultants[coluns], errors='coerce', format="%Y-%m-%d")
        
    df_consultants['presales_allocation'] = pd.to_numeric(df_consultants['presales_allocation']).fillna(0)
    
    for coluns in columns_object_consultants:
        df_consultants[coluns] = df_consultants[coluns].map(
            lambda x: str(x) if x not in [None, '', ' '] else 'N/A'
        )
    
    # Modificar o tipo das colunas do dataframe de alocação
    columns_date_allocation = ["start_date", "release_date"]
    columns_number_allocation = ['alocation', 'days', 'hour_cost', 'us_cost']
    colunas_object_allocation = df_allocation.select_dtypes(include='object').columns
    
    df_allocation[columns_number_allocation] = df_allocation[columns_number_allocation].apply(pd.to_numeric).fillna(0)

    for coluns in columns_date_allocation:
        df_allocation[coluns] = pd.to_datetime(df_allocation[coluns], errors='coerce', format="%Y-%m-%d")
    
    for coluns in colunas_object_allocation:
        df_allocation[coluns] = df_allocation[coluns].map(
            lambda x: str(x) if x not in [None, '', ' '] else 'N/A'
        )

def load_Data(df_consultants, df_allocation):
    df_consultants.to_csv('./load_test/consultants.csv', index=False)
    df_allocation.to_csv('./load_test/allocation.csv', index=False)

def consultant_allocation(df_area_consultants):
    board_id = config_data.boards_id["consultant_allocation"]
    schema_projects, data = request_consultants(board_id)
    new_schema_projects = ["employee_id"] + [
        column
        for column in schema_projects
        if not re.search(r'.*id.*',column.lower()) and column.lower() != 'subelementos'
    ]
    
    for item in data: #impede que os dados sejam armazenados como uma lista dentro de outra lista
        all_data.append(item)
    
    schema_subitems_consultants = ['employee_id','allocation','Status', 'Start Date', 'Release Date', 'Alocation', 'Days', 'Hour Cost', 'US$ Cost']
    
    extract_data_api(data, consultants_list,subitems_consultants_list)
    df_consultants, df_allocation = create_dataset(consultants_list, new_schema_projects,subitems_consultants_list, schema_subitems_consultants)
    
    df_consultants = df_consultants.drop_duplicates('employee_id')
    df_allocation = df_allocation.drop_duplicates(subset=["employee_id", "allocation"])
    df_consultants = define_area_consultants(df_consultants, df_area_consultants)
    df_consultants,df_allocation = rename_coluns_dataset(df_consultants,df_allocation)
    modify_type_column(df_consultants,df_allocation)
    
    load_Data(df_consultants, df_allocation)
    
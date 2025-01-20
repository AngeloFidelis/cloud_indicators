import pandas as pd
from config import ConfigData
from random import randint
import numpy as np

config_data = ConfigData()

def create_table(data, project_list, subitems_list):
    ...
    for items in data:
        opt = items["name"].split(' - ')[0]
        client = items["name"].split(' - ')[1]
        project_name = ' - '.join(items["name"].split(' - ')[2:])
        id_project = ''.join([opt.replace("-",''), str(randint(100000,999999))]) # Cria um id para o projeto com base na OPT
        project_info_rows = []
        subitems_by_project_info_rows = []
        
        #Esse primeiro for vai ordenar as informaçoes dos projetos
        for items_values in items['column_values']:
            project_info_rows.append(items_values['text'])
        
        #Esse segundo for vai ordenar as informaçoes dos consultores (subitems)
        for subitems in items['subitems']:
            row_values = []
            roles = subitems['name'].split(' - ')[0]
            for subitems_values in subitems['column_values']:
                row_values.append(subitems_values['text'])
            subitems_by_project_info_rows.append([id_project] + [roles] + row_values)
        current_project = [id_project] + [opt] + [client] +[project_name] + project_info_rows[1:]
        project_list.append(current_project)
        if subitems_by_project_info_rows.__len__() != 0:
            subitems_list.append(subitems_by_project_info_rows)
        
def create_dataset(project_list, subitems_list, new_schema_project, schema_subitems):
    
    subitems_list = [
        items for subitems in subitems_list for items in subitems
    ]
    df_project = pd.DataFrame(project_list, columns=new_schema_project)
    df_subitems = pd.DataFrame(subitems_list, columns=schema_subitems)
    
    return [df_project,df_subitems]

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
    
    df_project = df_project.rename(columns={'client': 'customer'})
    df_project = df_project.rename(columns={'subelementos': 'roles_needed'})
    
    df_subitems = df_subitems.rename(columns={'consultor': 'consultant'})
    df_subitems = df_subitems.rename(columns={'name': 'role'})

    return df_project,df_subitems

# Função que preenche dados nulos de formulas do monday
def fill_null_data_formula(df_project, df_subitems):
    ## ------------------------------ Formulas para calcular as horas e o custo ------------------------------
    df_subitems['hours'] = df_subitems.apply(
        lambda df: round(pd.to_numeric(df['working_days'], errors='coerce') * 8 / 100 * pd.to_numeric(df["allocation"], errors="coerce"), 2),
        axis=1
    )
    df_subitems['cost'] = pd.to_numeric(df_subitems['cost_per_hour']) * df_subitems['hours']
    df_subitems["role"] = df_subitems["role"].apply(lambda x: x.split(" - ")[0])
    
    ## ------------------------------ Salvar valores como 'working_days', 'cronograma', 'hours' e 'cost' na tabela 'df_project' ------------------------------
    for i, row_project in df_project.iterrows():
        matching_idproject = df_subitems[df_subitems['id_project'] == row_project['id_project']]
        if not matching_idproject.empty:
            cronograma = []
            
            working_days = pd.to_numeric(matching_idproject['working_days']).dropna().max()
            cronograma = [
                date 
                for interval 
                in matching_idproject['cronograma'] 
                for date
                in interval.split(' - ')
                if date
            ]
            
            # essa list compreension transofrma isso:
            # ['2024-01-29 - 2024-02-19', '2024-01-29 - 2024-02-19']
            # nisso:
            # ['2024-01-29', '2024-02-19', '2024-01-29', '2024-02-19']
            # O try except é usado para caso haja cronograma como null, não quebre a aplicação
            
            try:
                start_project = min(cronograma)
                end_project = max(cronograma)
                
                df_project.at[i,'start'] = df_project.at[i,"start"] if df_project.at[i,"start"] not in [None, "", " ", np.nan] else start_project 
                df_project.at[i,'end'] = df_project.at[i,"end"] if df_project.at[i,"end"] not in [None, "", " ", np.nan] else end_project 
            except ValueError as err:
                print(err)
                df_project.at[i,'start'] = np.nan
                df_project.at[i,'end'] = np.nan
                

            hours = matching_idproject['hours'].dropna().max() #pegar o valor maximo de horas
            cost = matching_idproject['cost'].dropna().sum()
            
            #o 'at' vai selecionar apenas as linhas cujos ids do df_project correspondam aos ids do df_subitems   
            df_project.at[i, 'working_days'] = working_days if working_days else 'N/A'
            df_project.at[i, 'hours'] = hours if hours else '0'
            df_project.at[i, 'cost'] = cost if cost else '0'
    
    ##  ------------------------------ Formula para calcular a margem ------------------------------
    df_project['margin'] = df_project.apply(
        lambda df: (pd.to_numeric(df['revenue'], errors='coerce') - pd.to_numeric(df['cost'], errors='coerce')) / pd.to_numeric(df['revenue'].replace("0",'1'), errors='coerce'),
        axis=1
    )
    
    return df_project, df_subitems

def split_cronograma(df_project, df_subitems):
    try:
        df_subitems[['schedule_start', 'schedule_end']] = df_subitems['cronograma'].str.split(' - ', expand=True)
    except:
        df_subitems[['schedule_start', 'schedule_end']] = None

    df_subitems = df_subitems.drop('cronograma', axis=1)
    df_project = df_project.drop('cronograma', axis=1)
    
    cols = df_subitems.columns.tolist()
    insert_at = cols.index('consultant') + 1
    cols = cols[:insert_at] + ['schedule_start', 'schedule_end'] + cols[insert_at:-2]
    df_subitems = df_subitems[cols]
    
    return df_project, df_subitems

def format_data(df_project, df_subitems): 
    
    # Formatar dados do project
    coluns_revenue_projects = df_project.filter(regex='revenue').columns
    coluns_margin_projects = df_project.filter(regex='margin').columns
    coluns_number_projects = ['cost', 'hours', 'working_days', 'advanced_onboarding', 'us$_monthly_consumption']
    
    for coluns in coluns_margin_projects:
        df_project[coluns] = pd.to_numeric(df_project[coluns], errors='coerce').fillna(0)
        df_project["margin"] = df_project["margin"].apply(lambda x: round(x,4)) #transforma a margin em porcentagem
    for coluns in coluns_revenue_projects:
        df_project[coluns] = pd.to_numeric(df_project[coluns], errors='coerce').fillna(0)
    
    for coluns in coluns_number_projects:
        df_project[coluns] = pd.to_numeric(df_project[coluns], errors='coerce').fillna(0)
    
    df_project["cost"] = df_project["cost"].apply(lambda x: round(x,2))
    df_project["start"] = pd.to_datetime(df_project["start"], errors='coerce', format="%Y-%m-%d")
    df_project["end"] = pd.to_datetime(df_project["end"], errors='coerce', format="%Y-%m-%d")
    
    colunas_object_project = df_project.select_dtypes(include='object').columns
    for coluns in colunas_object_project:
        df_project[coluns] = df_project[coluns].apply(
            lambda x: str(x) if x not in [None, '', ' '] else 'N/A'
        )
    
    # Formatar dados dos subitems
    
    coluns_number_subitems = ['allocation', 'working_days', 'hours', 'cost_per_hour', 'cost']
    for coluns in coluns_number_subitems:
        df_subitems[coluns] = pd.to_numeric(df_subitems[coluns], errors='coerce').fillna(0)
        
    df_subitems["schedule_start"] = pd.to_datetime(df_subitems["schedule_start"], errors='coerce', format="%Y-%m-%d")
    df_subitems["schedule_end"] = pd.to_datetime(df_subitems["schedule_end"], errors='coerce', format="%Y-%m-%d")
    
    
    colunas_object_subitems = df_subitems.select_dtypes(include='object').columns
    
    for coluns in colunas_object_subitems:
        df_subitems[coluns] = df_subitems[coluns].apply(
            lambda x: str(x) if x not in [None, '', ' '] else 'N/A'
        )
    
    return df_project, df_subitems

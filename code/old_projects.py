from request_api import request_projects
import time
from transform_data import config_data, create_table, create_dataset, rename_coluns_dataset, fill_null_data_formula, split_cronograma, format_data

project_list = []
subitems_list = []

def load_data(df_project, df_subitems):
    df_project.to_csv(f"./load_test/df_projects_old.csv", index=False)
    df_subitems.to_csv(f"./load_test/df_subitems_old.csv", index=False)

def old_projects():
    begin = time.time()
    board_id = config_data.boards_id["old_projects"]
    data, schema_projects = request_projects(board_id)
    new_schema_project = ['id_project', 'opt', 'client'] + [
        'project_name' if header == 'Name' else header and 'US$ Monthly consumption' if header == 'US$ Monthly consuption' else header
        for header in schema_projects
        if header != "Subelementos"
    ]
    
    schema_subitems = ['id_project', 'name', 'Consultor', 'Cronograma', 'Billable', 'Allocation', 'Working Days', 'Hours', 'Cost per Hour', 'Cost']
    
    create_table(data, project_list, subitems_list)
    df_project,df_subitems = create_dataset(project_list, subitems_list, new_schema_project, schema_subitems)
    df_project,df_subitems = rename_coluns_dataset(df_project,df_subitems)
    df_project,df_subitems = fill_null_data_formula(df_project, df_subitems)
    df_project, df_subitems = split_cronograma(df_project, df_subitems)
    df_project, df_subitems = format_data(df_project, df_subitems)
    load_data(df_project, df_subitems)
    print(f"Tempo de execução do programa: {round(time.time() - begin, 2)} segundos")
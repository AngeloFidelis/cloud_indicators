import pandas as pd
import hashlib
import re

test = [[1,2,3],[4,5,6],[7,8,9]]
test2 = [
    
    item
    for items 
    in test
    for item
    in items
]
# print(test2)

name = ['OPT-1335', 'Grupo Boticário', 'Engenheiro Apigee']
a1,a2,a3 = name
# print(a1)

# print(hashlib.sha256().hexdigest())

test5 = 'OPT-0349 - Tembici - #3 - IOT Platform (SVET) - Março'

opt = test5.split(' - ')[0]
Client = test5.split(' - ')[1]
Project_name = ' - '.join(test5.split(' - ')[2:])
# print(opt)
# print(Client)
# print(Project_name)

dataframe_test = {
    "id": [123,456,123,678],
    'name': ['Angelo', 'Pedro', 'angelo', 'Joao']
}

dataframe = pd.DataFrame(dataframe_test)
dataframe = dataframe.drop_duplicates('id')

dataframe_test2 = [
    ['valor11', 'valor12', 'valor13'],
    ['valor21', 'valor22', 'valor23'],
    ['valor13', 'valor32', 'valor33']
]
dataframe_test3 = [
    ['valor113', 'valor12', 'valor13'],
    ['valor21', 'valor22'],
    ['valor133', 'valor32', 'valor33']
]

dataframe_concat = dataframe_test2 + dataframe_test3
schema_test = ['schema1','schema2','schema3']

dataframe2 = pd.DataFrame(dataframe_concat, columns=schema_test)
dataframe2 = dataframe2.drop_duplicates('schema1')
print(dataframe2)
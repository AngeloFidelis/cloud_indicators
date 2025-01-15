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
print(opt)
print(Client)
print(Project_name)

cronograma.append(
        [
            cron.split(' - ')
            for cron 
            in matching_idproject['cronograma'] 
            if cron
        ]
    )
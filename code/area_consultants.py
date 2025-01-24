import os.path
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
from secret import secrets
from config import ConfigData
import json

config_data = ConfigData()
request_key = secrets(config_data.project_id) #Chama a função 'secrets' passando o 'project_id' da configuração.
api_sheet = request_key(config_data.service_account, config_data.version)

api_sheet = json.loads(api_sheet)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SAMPLE_SPREADSHEET_ID = config_data.spreadsheet_id
SAMPLE_RANGE_NAME = config_data.range_name

# pd.set_option('display.max_rows', None)

def area_consultants():
    processed_data = []
    credentials = service_account.Credentials.from_service_account_info(
        api_sheet, scopes=SCOPES
    )
    
    service = build("sheets", "v4", credentials=credentials)
    
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
        .execute()
    )
    values = result.get("values", [])
    
    for row in values:
        if len(row) == 1:
            current_area = row[0]
        elif len(row) > 1 and row[0] != "Name" and row[0] != "":
            processed_data.append({
                "Name": row[0],
                "Area": current_area,
                "employee_id": row[4],
                "AC_situation": row[13],
            })
    df = pd.DataFrame(processed_data)
    df_actives = df[df["AC_situation"] == "Active"]
    return df
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import json

with open('secrets.json') as f:
    secrets = json.load(f)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


def get_sheets_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                secrets['google']['credentials_file'], SCOPES)
            creds = flow.run_local_server(port=8080)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)
    return service

def read_sheet_data(spreadsheet_id, range_name):
    service = get_sheets_service()
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])
    return values

def get_sheet_last_update(spreadsheet_id):
    service = get_sheets_service()
    sheet = service.spreadsheets()
    result = sheet.get(spreadsheetId=spreadsheet_id).execute()
    print("result:", result)
    last_modified = result.get('modifiedTime')
    return last_modified

def update_google_sheet(spreadsheet_id, range_name, values):
    service = get_sheets_service()
    sheet = service.spreadsheets()
    body = {
        'values': values
    }
    result = sheet.values().update(spreadsheetId=spreadsheet_id, range=range_name, valueInputOption='RAW', body=body).execute()
    print(f"Updated {result.get('updatedCells')} cells.")

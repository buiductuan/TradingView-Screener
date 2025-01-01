import os
import numpy as np
from fastapi import Request
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()
SCOPES = os.getenv('SCOPES', 'https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/drive').split(',')
CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE', 'secret.json')
REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://127.0.0.1:8000/oauth2callback')

def authorize():
    credentials = None
    try:
        credentials = Credentials.from_authorized_user_file(
            'token.json', SCOPES)
        return {
            "is_redirect": False,
            "credentials": credentials
        }
    except Exception:
        flow = Flow.from_client_secrets_file(
            CREDENTIALS_FILE,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        auth_url, _ = flow.authorization_url(prompt="consent")
        return {
            "is_redirect": True,
            "auth_url": auth_url
        }


def oauth2callback(request: Request):
    query_params = dict(request.query_params)
    credentials = None
    try:
        credentials = Credentials.from_authorized_user_file(
            'token.json', SCOPES)
    except Exception:
        flow = Flow.from_client_secrets_file(
            CREDENTIALS_FILE,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        flow.fetch_token(code=query_params.get("code"))
        credentials = flow.credentials
        
        # Save token
        with open('token.json', 'w') as token:
            token.write(credentials.to_json())
    return credentials


def write_to_google_sheets(credentials, spreadsheet_id, sheet_range, data):
    try:
        service = build("sheets", "v4", credentials=credentials)
        data = data.replace({np.nan: None})
        # Add headers [list(data.columns)]
        values = data.values.tolist()
        body = {"values": values}
        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=sheet_range,
            valueInputOption="RAW",
            body=body
        ).execute()
    except Exception:
        authorize()

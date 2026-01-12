"""
Google Sheets helper functions.
Handles authentication and common operations with Google Sheets.
"""

import os
import pickle
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file'
]


def authenticate_google():
    """
    Authenticate with Google API and return credentials.

    Returns:
        Credentials object for Google API

    Raises:
        FileNotFoundError: If credentials.json is not found
    """
    creds = None

    # The file token.json stores the user's access and refresh tokens
    token_path = Path('token.json')
    credentials_path = Path('credentials.json')

    if not credentials_path.exists():
        raise FileNotFoundError(
            "credentials.json not found. "
            "Please download it from Google Cloud Console and place it in the root directory."
        )

    # Check if we have valid credentials stored
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    # If no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save credentials for next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return creds


def get_sheets_service():
    """
    Get authenticated Google Sheets service.

    Returns:
        Google Sheets service object
    """
    creds = authenticate_google()
    service = build('sheets', 'v4', credentials=creds)
    return service


def create_spreadsheet(title):
    """
    Create a new Google Spreadsheet.

    Args:
        title (str): Title for the new spreadsheet

    Returns:
        dict: Spreadsheet metadata including ID and URL
    """
    try:
        service = get_sheets_service()
        spreadsheet = {
            'properties': {
                'title': title
            }
        }

        spreadsheet = service.spreadsheets().create(
            body=spreadsheet,
            fields='spreadsheetId,spreadsheetUrl'
        ).execute()

        print(f"✓ Created spreadsheet: {spreadsheet.get('spreadsheetUrl')}")
        return spreadsheet

    except HttpError as error:
        print(f"✗ Error creating spreadsheet: {error}")
        raise


def write_to_sheet(spreadsheet_id, range_name, values):
    """
    Write values to a Google Sheet.

    Args:
        spreadsheet_id (str): ID of the spreadsheet
        range_name (str): A1 notation range (e.g., 'Sheet1!A1:D10')
        values (list): 2D list of values to write

    Returns:
        dict: Update response
    """
    try:
        service = get_sheets_service()

        body = {
            'values': values
        }

        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()

        print(f"✓ Updated {result.get('updatedCells')} cells")
        return result

    except HttpError as error:
        print(f"✗ Error writing to sheet: {error}")
        raise


def read_from_sheet(spreadsheet_id, range_name):
    """
    Read values from a Google Sheet.

    Args:
        spreadsheet_id (str): ID of the spreadsheet
        range_name (str): A1 notation range (e.g., 'Sheet1!A1:D10')

    Returns:
        list: 2D list of values
    """
    try:
        service = get_sheets_service()

        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()

        values = result.get('values', [])
        print(f"✓ Read {len(values)} rows")
        return values

    except HttpError as error:
        print(f"✗ Error reading from sheet: {error}")
        raise


def append_to_sheet(spreadsheet_id, range_name, values):
    """
    Append values to a Google Sheet.

    Args:
        spreadsheet_id (str): ID of the spreadsheet
        range_name (str): A1 notation range (e.g., 'Sheet1!A:D')
        values (list): 2D list of values to append

    Returns:
        dict: Append response
    """
    try:
        service = get_sheets_service()

        body = {
            'values': values
        }

        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()

        print(f"✓ Appended {len(values)} rows")
        return result

    except HttpError as error:
        print(f"✗ Error appending to sheet: {error}")
        raise


if __name__ == "__main__":
    # Test authentication
    print("Testing Google Sheets authentication...")
    try:
        service = get_sheets_service()
        print("✓ Successfully authenticated with Google Sheets")
    except Exception as e:
        print(f"✗ Authentication failed: {e}")

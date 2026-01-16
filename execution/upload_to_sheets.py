"""
Upload SA cleaning leads to Google Sheets using gcp-oauth credentials
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path to import google_sheets_helper
sys.path.insert(0, str(Path(__file__).parent))

# Set the Google credentials path
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Volumes/MortAihq/MortaiHQ/Agentic Agents /anti grav workflows/Lead scraper : cold email sender /gcp-oauth.keys.json'

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    import pickle
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Installing required packages...")
    os.system("pip3 install --user google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    import pickle

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.file']

def get_credentials():
    """Get or create credentials."""
    creds = None
    token_path = Path.home() / '.config/google-drive-mcp/tokens.json'

    # Try to load existing token
    if token_path.exists():
        try:
            with open(token_path, 'r') as token:
                token_data = json.load(token)
                creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        except Exception as e:
            print(f"Could not load existing token: {e}")

    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            print("Starting OAuth flow...")
            oauth_path = Path('/Volumes/MortAihq/MortaiHQ/Agentic Agents /anti grav workflows/Lead scraper : cold email sender /gcp-oauth.keys.json')

            if not oauth_path.exists():
                print(f"Error: OAuth credentials not found at {oauth_path}")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(str(oauth_path), SCOPES)
            creds = flow.run_local_server(port=0)

            # Save credentials
            token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
            print(f"Credentials saved to {token_path}")

    return creds

def create_sheet_with_data():
    """Create Google Sheet with SA cleaning leads."""

    # Get credentials
    creds = get_credentials()
    if not creds:
        print("Failed to get credentials")
        return None

    # Build service
    service = build('sheets', 'v4', credentials=creds)

    # Create spreadsheet
    spreadsheet = {
        'properties': {
            'title': 'SA Commercial Cleaning Leads - Test Scrape'
        }
    }

    spreadsheet = service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId,spreadsheetUrl').execute()
    spreadsheet_id = spreadsheet['spreadsheetId']

    print(f"✅ Created spreadsheet: {spreadsheet['spreadsheetUrl']}")

    # Prepare data
    data = [
        ["Company Name", "Website", "Email 1", "Email 2", "Email 3", "Employee Count", "Services Offered", "Commercial Cleaning", "Notes"],
        ["Bidvest Prestige Cleaning", "https://www.bidvestprestige.co.za", "craigd@presclean.co.za", "karen@presclean.co.za", "riette@presclean.co.za", "1000+", "Commercial cleaning, office cleaning, industrial cleaning", "Yes", "Major commercial cleaning provider in SA, part of Bidvest Group"],
        ["Tsebo Outsourcing Group", "https://www.tsebo.com", "cleaning@tsebo.com", "info@tsebo.com", "", "50,000+", "Facilities management, commercial cleaning, catering", "Yes", "Largest facilities management company in Africa"],
        ["ServiceMaster South Africa", "https://www.servicemaster.co.za", "customercare@servicemaster.co.za", "", "", "500+", "Commercial cleaning, disaster restoration, facility services", "Yes", "International brand with strong SA presence"],
        ["Initial Hygiene South Africa", "https://www.initial.co.za", "sales@initial.co.za", "info@initial.co.za", "", "800+", "Hygiene services, washroom services, commercial cleaning", "Yes", "Part of Rentokil Initial, leading hygiene services provider"],
        ["PHS Group South Africa", "https://www.phs.co.za", "info@phs.co.za", "", "", "300+", "Washroom services, hygiene solutions, commercial cleaning", "Yes", "UK-based company with SA operations"],
        ["Procare Cleaning Services", "https://www.procarecleaning.co.za", "info@procarecleaning.co.za", "admin@procarecleaning.co.za", "", "200+", "Office cleaning, carpet cleaning, window cleaning, industrial cleaning", "Yes", "Established commercial cleaning company serving Johannesburg and Pretoria"],
        ["CleanCo Services", "https://www.cleanco.co.za", "bookings@cleanco.co.za", "info@cleanco.co.za", "", "150+", "Commercial cleaning, office cleaning, industrial cleaning", "Yes", "Serves corporate clients across major SA cities"],
        ["JAN-PRO South Africa", "https://www.jan-pro.co.za", "info@jan-pro.co.za", "", "", "100+", "Office cleaning, medical facility cleaning, commercial cleaning", "Yes", "International franchise with SA operations, focuses on healthcare and office cleaning"],
        ["Bee Clean Commercial Cleaning", "https://www.beeclean.co.za", "admin@beeclean.co.za", "info@beeclean.co.za", "", "80+", "Office cleaning, retail cleaning, medical practice cleaning", "Yes", "Specializes in small to medium business cleaning"],
        ["A-Len Cleaning & Support Services", "https://www.alen.co.za", "sales@alen.co.za", "info@alen.co.za", "", "500+", "Commercial cleaning, facilities management, industrial cleaning", "Yes", "BEE Level 1 certified, major corporate clients"]
    ]

    # Write data
    body = {'values': data}
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range='Sheet1!A1',
        valueInputOption='RAW',
        body=body
    ).execute()

    print(f"✅ Updated {result.get('updatedCells')} cells")
    print(f"\n📊 Google Sheet URL: {spreadsheet['spreadsheetUrl']}")

    return spreadsheet

if __name__ == "__main__":
    print("=" * 70)
    print("📊 UPLOADING SA CLEANING LEADS TO GOOGLE SHEETS")
    print("=" * 70)
    print()

    spreadsheet = create_sheet_with_data()

    if spreadsheet:
        print("\n✅ SUCCESS!")
        print(f"Your leads are now in Google Sheets: {spreadsheet['spreadsheetUrl']}")
    else:
        print("\n❌ Failed to create Google Sheet")

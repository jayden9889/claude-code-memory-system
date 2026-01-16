#!/usr/bin/env python3
"""
Export the final 10 B2B cleaning leads to Google Sheets.
"""

import csv
from pathlib import Path
import time
from google_sheets_helper import create_spreadsheet, write_to_sheet

def export_leads_to_sheets():
    """Read CSV and export to Google Sheets."""
    
    # Read the CSV
    csv_path = Path('.tmp/b2b_cleaning_leads_final_10.csv')
    
    if not csv_path.exists():
        print(f"❌ CSV file not found: {csv_path}")
        return None
    
    print("📄 Reading CSV file...")
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    print(f"✓ Read {len(rows)} rows (including header)\n")
    
    # Create Google Sheet
    sheet_title = f"B2B Cleaning Leads - {time.strftime('%Y-%m-%d %H:%M')}"
    print(f"📊 Creating Google Sheet: {sheet_title}")
    
    try:
        spreadsheet = create_spreadsheet(sheet_title)
        spreadsheet_id = spreadsheet['spreadsheetId']
        spreadsheet_url = spreadsheet['spreadsheetUrl']
        
        # Write data
        print("\n📝 Writing data to sheet...")
        write_to_sheet(spreadsheet_id, 'Sheet1!A1', rows)
        
        print("\n" + "=" * 70)
        print("✅ EXPORT COMPLETE!")
        print("=" * 70)
        print(f"\n📊 Google Sheet URL:")
        print(f"   {spreadsheet_url}")
        print(f"\n📋 Total leads exported: {len(rows) - 1}")
        print()
        
        return spreadsheet
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\n⚠️  Google Sheets credentials not found.")
        print("   Please set up Google OAuth credentials first.")
        print("   For now, the data is available in CSV format at:")
        print(f"   {csv_path}")
        return None
    except Exception as e:
        print(f"\n❌ Error exporting to Google Sheets: {e}")
        print(f"   Data is still available in CSV format at: {csv_path}")
        return None

if __name__ == "__main__":
    print("=" * 70)
    print("📊 EXPORTING B2B CLEANING LEADS TO GOOGLE SHEETS")
    print("=" * 70)
    print()
    
    spreadsheet = export_leads_to_sheets()
    
    if spreadsheet:
        print("🎉 Success! Your leads are now in Google Sheets.")
    else:
        print("\n📄 CSV file is available for manual upload if needed.")

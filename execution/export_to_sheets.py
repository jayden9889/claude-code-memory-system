"""
Export validated leads to Google Sheets.
Creates a new spreadsheet or updates an existing one.
"""

import sys
from datetime import datetime
from utils import load_json, log_error, log_success
from google_sheets_helper import (
    create_spreadsheet,
    write_to_sheet,
    append_to_sheet
)


def prepare_sheet_data(leads):
    """
    Convert lead dictionaries to 2D array for Google Sheets.

    Args:
        leads (list): List of lead dictionaries

    Returns:
        list: 2D array with header row and data rows
    """
    if not leads:
        return [['No leads to export']]

    # Define column headers
    headers = [
        'First Name',
        'Last Name',
        'Email',
        'Title',
        'LinkedIn URL',
        'Company Name',
        'Company Domain',
        'Company Industry',
        'Company Size',
        'City',
        'State',
        'Country',
        'Status'
    ]

    # Convert leads to rows
    rows = [headers]

    for lead in leads:
        row = [
            lead.get('first_name', ''),
            lead.get('last_name', ''),
            lead.get('email', ''),
            lead.get('title', ''),
            lead.get('linkedin_url', ''),
            lead.get('company_name', ''),
            lead.get('company_domain', ''),
            lead.get('company_industry', ''),
            str(lead.get('company_size', '')),
            lead.get('city', ''),
            lead.get('state', ''),
            lead.get('country', ''),
            lead.get('validation_status', 'valid')
        ]
        rows.append(row)

    return rows


def export_leads(leads, spreadsheet_title=None):
    """
    Export leads to a new Google Spreadsheet.

    Args:
        leads (list): List of lead dictionaries
        spreadsheet_title (str): Optional title for the spreadsheet

    Returns:
        dict: Spreadsheet info with ID and URL
    """
    try:
        # Generate title if not provided
        if not spreadsheet_title:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            spreadsheet_title = f"Leads Export - {timestamp}"

        # Create new spreadsheet
        spreadsheet = create_spreadsheet(spreadsheet_title)
        spreadsheet_id = spreadsheet['spreadsheetId']
        spreadsheet_url = spreadsheet['spreadsheetUrl']

        # Prepare data
        sheet_data = prepare_sheet_data(leads)

        # Write to sheet
        range_name = 'Sheet1!A1'
        write_to_sheet(spreadsheet_id, range_name, sheet_data)

        log_success(
            f"Exported {len(leads)} leads to Google Sheets",
            {
                'spreadsheet_id': spreadsheet_id,
                'url': spreadsheet_url,
                'rows': len(sheet_data)
            }
        )

        return {
            'spreadsheet_id': spreadsheet_id,
            'spreadsheet_url': spreadsheet_url,
            'lead_count': len(leads)
        }

    except Exception as e:
        log_error(f"Failed to export leads: {e}")
        raise


def main(input_file='leads_validated.json', title=None):
    """
    Load validated leads and export to Google Sheets.

    Args:
        input_file (str): Input JSON file in .tmp/
        title (str): Optional spreadsheet title
    """
    try:
        # Load validated leads
        leads = load_json(input_file)
        print(f"Loaded {len(leads)} validated leads from {input_file}")

        # Export to Google Sheets
        result = export_leads(leads, title)

        # Print results
        print(f"\n{'='*60}")
        print(f"✓ Export Complete")
        print(f"{'='*60}")
        print(f"Spreadsheet URL: {result['spreadsheet_url']}")
        print(f"Lead Count: {result['lead_count']}")
        print(f"{'='*60}\n")

        return result

    except FileNotFoundError as e:
        log_error(f"Input file not found: {e}")
        print("\nMake sure you've run validate_leads.py first!")
        sys.exit(1)
    except Exception as e:
        log_error(f"Export failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Export leads to Google Sheets')
    parser.add_argument(
        '--input',
        default='leads_validated.json',
        help='Input JSON file in .tmp/ directory'
    )
    parser.add_argument(
        '--title',
        help='Spreadsheet title (default: auto-generated with timestamp)'
    )

    args = parser.parse_args()
    main(args.input, args.title)

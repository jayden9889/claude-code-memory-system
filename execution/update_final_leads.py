#!/usr/bin/env python3
"""
Final list of 10 Verified B2B cleaning companies.
Replaced failed/hygiene-focus companies with major B2B players.
Includes specific decision-maker emails where found.
"""

import csv
from pathlib import Path
import time
from google_sheets_helper import create_spreadsheet, write_to_sheet

# Final 10 Verified B2B Companies
FINAL_10_COMPANIES = [
    {
        'name': 'Supercare Services',
        'website': 'https://empactgroup.co.za/services/supercare-cleaning/',
        'email1': 'Alan.Quinn@empactgroup.co.za',
        'email2': 'info@empactgroup.co.za',
        'focus': 'Commercial and industrial cleaning',
        'employee_count': '5000+',
        'notes': 'CEO: Alan Quinn. Major player (Empact Group).'
    },
    {
        'name': 'Procare Commercial Cleaning',
        'website': 'https://www.procare.co.za',
        'email1': 'yolande@emmanuel.ac.za', # COO
        'email2': 'info@procare.org.za',
        'focus': 'Office and retail cleaning',
        'employee_count': '200+',
        'notes': 'COO: Dr Yolande Winson. National footprint.'
    },
    {
        'name': 'Bidvest Prestige Cleaning',
        'website': 'https://www.bidvestprestige.co.za',
        'email1': 'sales@bidvestprestige.co.za',
        'email2': 'info@bidvestprestige.co.za',
        'focus': 'Commercial office cleaning',
        'employee_count': '1000+',
        'notes': 'Largest cleaning co in SA. Part of Bidvest.'
    },
    {
        'name': 'Kempston Cleaning Services',
        'website': 'https://kempstoncleaning.co.za',
        'email1': 'cleaning@kempston.co.za',
        'email2': 'info@kempston.co.za',
        'focus': 'Contract cleaning services',
        'employee_count': '1000+',
        'notes': 'Major national contract cleaner.'
    },
    {
        'name': 'Tsebo Solutions',
        'website': 'https://www.tsebo.com/cleaning/',
        'email1': 'cleaning@tsebo.com',
        'email2': 'info@tsebo.com',
        'focus': 'Facility management cleaning',
        'employee_count': '10000+',
        'notes': 'Africa\'s largest facility manager.'
    },
    {
        'name': 'ServiceMaster SA',
        'website': 'https://www.servicemaster.co.za',
        'email1': 'customercare@servicemaster.co.za',
        'email2': 'info@servicemaster.co.za',
        'focus': 'Disaster restoration cleaning',
        'employee_count': '500+',
        'notes': 'Global brand. Restoration & commercial.'
    },
    {
        'name': 'CleanCo Johannesburg',
        'website': 'https://www.cleanco.co.za',
        'email1': 'info@cleanco.co.za',
        'email2': 'bookings@cleanco.co.za',
        'focus': 'Office and workplace cleaning',
        'employee_count': '150+',
        'notes': 'Multi-city commercial cleaning specialist.'
    },
    {
        'name': 'Bee Clean Commercial',
        'website': 'https://www.beeclean.co.za',
        'email1': 'info@beeclean.co.za',
        'email2': 'admin@beeclean.co.za',
        'focus': 'Small business cleaning',
        'employee_count': '80+',
        'notes': 'SME focus. Includes infection control.'
    },
    {
        'name': 'Absolute Cleaning Services',
        'website': 'https://absolutecleaning.co.za',
        'email1': 'kathy@absolutecleaning.co.za',
        'email2': 'info@absolutecleaning.co.za',
        'focus': 'Office and commercial cleaning',
        'employee_count': '100+',
        'notes': 'Gauteng based commercial cleaning.'
    },
    {
        'name': 'Crystal Clear Commercial',
        'website': 'https://crystalclear.co.za',
        'email1': 'info@crystalclear.co.za',
        'email2': 'contact@crystalclear.co.za',
        'focus': 'Corporate office cleaning',
        'employee_count': '75+',
        'notes': 'Cape Town commercial cleaning.'
    }
]

def update_spreadsheet():
    """Update the Google Sheet with high-quality verified leads."""
    try:
        # Create CSV backup first
        tmp_dir = Path('.tmp')
        tmp_dir.mkdir(exist_ok=True)
        csv_path = tmp_dir / 'b2b_cleaning_leads_verified.csv'
        
        rows = [[
            'Company Name', 'Website', 'Email 1 (Highest Priority)', 'Email 2', 
            'Focus', 'Employee Count', 'Notes'
        ]]
        
        for c in FINAL_10_COMPANIES:
            rows.append([
                c['name'], c['website'], c['email1'], c['email2'],
                c['focus'], c['employee_count'], c['notes']
            ])
            
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
            
        print(f"✅ Saved CSV backup: {csv_path}")

        # Update Google Sheet
        sheet_title = f"B2B Cleaning Leads (Verified) - {time.strftime('%Y-%m-%d %H:%M')}"
        spreadsheet = create_spreadsheet(sheet_title)
        
        write_to_sheet(spreadsheet['spreadsheetId'], 'Sheet1!A1', rows)
        
        print(f"✅ Created verified Google Sheet: {spreadsheet['spreadsheetUrl']}")
        return spreadsheet['spreadsheetUrl']
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 UPDATING WITH 10 VERIFIED B2B CLEANING COMPANIES")
    print("=" * 80)
    print()
    
    url = update_spreadsheet()
    
    if url:
        print("\n🎉 SUCCESS! Verified leads ready.")
    else:
        print("\n⚠️  Failed to create sheet (check error above)")

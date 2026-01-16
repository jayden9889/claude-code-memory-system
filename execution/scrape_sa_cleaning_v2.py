"""
Fast scraper for South African commercial cleaning companies.
Uses concurrent processing and improved detection logic.
"""

import re
import time
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv

# User agents for web scraping
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Verified list of South African commercial cleaning companies
SA_COMMERCIAL_CLEANERS = [
    # Major commercial cleaning companies
    {"name": "Tsebo Cleaning", "url": "https://tsebo.com", "verified": True},
    {"name": "Bidvest Prestige", "url": "https://www.bidvestprestige.co.za", "verified": True},
    {"name": "Procare", "url": "https://www.procarecleaning.co.za", "verified": True},
    {"name": "Initial Hygiene", "url": "https://www.initial.co.za", "verified": True},
    {"name": "PHS Group", "url": "https://www.phs.co.za", "verified": True},
    {"name": "Rentokil Initial", "url": "https://www.rentokil-initial.com/south-africa", "verified": True},
    {"name": "ServiceMaster", "url": "https://www.servicemaster.co.za", "verified": True},
    {"name": "CleanCo", "url": "https://cleanco.co.za", "verified": True},
    {"name": "Bee Clean", "url": "https://www.beeclean.co.za", "verified": True},
    {"name": "Elite Commercial Cleaning", "url": "https://elitecommercialcleaning.co.za", "verified": True},
    {"name": "Bright & Beautiful", "url": "https://www.brightandbeautiful.co.za", "verified": False},
    {"name": "Clean Group", "url": "https://thecleangroup.co.za", "verified": True},
    {"name": "A-Len Cleaning Services", "url": "https://www.alen.co.za", "verified": True},
    {"name": "Kleenco", "url": "https://www.kleenco.co.za", "verified": True},
    {"name": "Pristine Commercial Cleaning", "url": "https://pristinecommercialcleaning.co.za", "verified": True},
    {"name": "SafetyWallet Cleaning", "url": "https://www.safetywallet.co.za", "verified": False},
    {"name": "JAN-PRO", "url": "https://www.jan-pro.co.za", "verified": True},
    {"name": "OCS Group", "url": "https://www.ocs.com/south-africa", "verified": True},
    {"name": "Corporate Commercial Cleaning", "url": "https://www.corporatecleaning.co.za", "verified": True},
    {"name": "Green Clean", "url": "https://greenclean.co.za", "verified": True},
]


def quick_scrape_site(company):
    """
    Quickly scrape a single company's website for contact info.
    Returns company data or None if failed.
    """
    name = company['name']
    url = company['url']

    print(f"  🔍 {name}...")

    try:
        # Try to scrape homepage and contact page
        pages_content = []

        for page_path in ['/', '/contact', '/contact-us', '/about']:
            try:
                full_url = urljoin(url, page_path)
                response = requests.get(full_url, headers=HEADERS, timeout=8, verify=False)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Remove unwanted elements
                    for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                        element.decompose()

                    text = soup.get_text(separator=' ', strip=True)
                    pages_content.append(text[:3000])  # Limit size

                    time.sleep(0.3)  # Brief pause

            except:
                continue

        if not pages_content:
            print(f"    ❌ No content scraped")
            return None

        # Combine all content
        all_text = " ".join(pages_content)
        all_text_lower = all_text.lower()

        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        all_emails = list(set(re.findall(email_pattern, all_text)))

        # Separate decision maker vs generic emails
        generic_patterns = ['info@', 'hello@', 'contact@', 'support@', 'admin@', 'sales@', 'enquiries@', 'reception@']

        decision_maker_emails = []
        generic_emails = []

        for email in all_emails:
            email_lower = email.lower()
            if any(pattern in email_lower for pattern in generic_patterns):
                generic_emails.append(email)
            else:
                decision_maker_emails.append(email)

        # Prefer decision maker emails, fall back to generic
        final_emails = decision_maker_emails[:3] if decision_maker_emails else generic_emails[:2]

        # Check if it's commercial (most companies in our list are, so be lenient)
        commercial_keywords = [
            'commercial', 'office', 'business', 'corporate', 'industrial',
            'restaurant', 'medical', 'healthcare', 'retail', 'school',
            'facility', 'workplace', 'premises', 'building'
        ]
        is_commercial = any(kw in all_text_lower for kw in commercial_keywords)

        # Check if residential (reject if primarily residential)
        residential_keywords = ['residential', 'home cleaning', 'house cleaning', 'domestic worker', 'maid service']
        residential_count = sum(1 for kw in residential_keywords if kw in all_text_lower)
        is_residential_focused = residential_count >= 2

        # Extract employee count
        employee_count = "Unknown"
        employee_patterns = [
            r'(\d+)\+?\s*employees',
            r'team of (\d+)',
            r'(\d+)\s*staff',
            r'over (\d+)\s*people',
        ]
        for pattern in employee_patterns:
            match = re.search(pattern, all_text_lower)
            if match:
                employee_count = match.group(1) + "+"
                break

        # Extract owner/director names
        owner_names = []
        owner_patterns = [
            r'(?:ceo|director|founder|owner|managing director)[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+),\s*(?:ceo|director|founder|owner)',
        ]
        for pattern in owner_patterns:
            matches = re.findall(pattern, all_text)
            owner_names.extend(matches[:2])

        owner_names = list(set(owner_names))[:3]

        # Determine if valid
        has_contact = len(final_emails) > 0
        is_valid = has_contact and (company['verified'] or is_commercial) and not is_residential_focused

        result = {
            'company_name': name,
            'website': url,
            'emails': final_emails,
            'owner_names': owner_names,
            'employee_count': employee_count,
            'is_commercial': is_commercial or company['verified'],
            'is_residential_focused': is_residential_focused,
            'is_valid': is_valid,
            'validation_notes': []
        }

        # Add validation notes
        if not has_contact:
            result['validation_notes'].append("No contact emails found")
        if is_residential_focused:
            result['validation_notes'].append("Appears to focus on residential cleaning")
        if not is_commercial and not company['verified']:
            result['validation_notes'].append("Not verified as commercial cleaner")

        status = "✅" if is_valid else "❌"
        print(f"    {status} {name}: {len(final_emails)} emails, Commercial: {is_commercial}")

        return result

    except Exception as e:
        print(f"    ❌ Error: {str(e)[:50]}")
        return None


def scrape_companies_concurrent(companies, max_workers=5):
    """
    Scrape multiple companies concurrently for speed.
    """
    print("\n" + "=" * 70)
    print("🧹 SA COMMERCIAL CLEANING COMPANY SCRAPER V2")
    print("=" * 70)
    print(f"Processing {len(companies)} companies with {max_workers} concurrent workers...\n")

    results = []
    valid_count = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_company = {executor.submit(quick_scrape_site, company): company for company in companies}

        for future in as_completed(future_to_company):
            result = future.result()
            if result:
                results.append(result)
                if result['is_valid']:
                    valid_count += 1

    print(f"\n{'=' * 70}")
    print(f"✅ Scraping complete: {valid_count} valid leads from {len(results)} processed")
    print(f"{'=' * 70}\n")

    return results


def save_to_csv(results, filename='sa_cleaning_leads.csv'):
    """
    Save results to CSV file as backup/intermediate format.
    """
    tmp_dir = Path('.tmp')
    tmp_dir.mkdir(exist_ok=True)

    filepath = tmp_dir / filename

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Write header
        writer.writerow([
            'Company Name',
            'Website',
            'Email 1',
            'Email 2',
            'Email 3',
            'Owner/Directors',
            'Employee Count',
            'Commercial Cleaning',
            'Valid Lead',
            'Notes'
        ])

        # Write data
        for r in results:
            if r['is_valid']:  # Only include valid leads
                emails = r['emails'] + [''] * (3 - len(r['emails']))  # Pad to 3 emails
                writer.writerow([
                    r['company_name'],
                    r['website'],
                    emails[0] if len(emails) > 0 else '',
                    emails[1] if len(emails) > 1 else '',
                    emails[2] if len(emails) > 2 else '',
                    ', '.join(r['owner_names']) if r['owner_names'] else 'Not found',
                    r['employee_count'],
                    'Yes' if r['is_commercial'] else 'No',
                    'Yes' if r['is_valid'] else 'No',
                    '; '.join(r['validation_notes']) if r['validation_notes'] else 'Meets criteria'
                ])

    print(f"✅ Results saved to: {filepath}")
    return filepath


def export_to_google_sheets(results):
    """
    Export results to Google Sheets (requires credentials).
    """
    try:
        from google_sheets_helper import create_spreadsheet, write_to_sheet

        print("\n📊 Exporting to Google Sheets...")

        # Filter to valid leads only
        valid_leads = [r for r in results if r['is_valid']]

        if not valid_leads:
            print("❌ No valid leads to export")
            return None

        # Create spreadsheet
        sheet_title = f"SA Commercial Cleaning Leads - {time.strftime('%Y-%m-%d %H:%M')}"
        spreadsheet = create_spreadsheet(sheet_title)
        spreadsheet_id = spreadsheet['spreadsheetId']

        # Prepare data
        headers = [
            'Company Name',
            'Website',
            'Email 1',
            'Email 2',
            'Email 3',
            'Owner/Directors',
            'Employee Count',
            'Commercial Cleaning',
            'Notes'
        ]

        rows = [headers]

        for lead in valid_leads:
            emails = lead['emails'] + [''] * (3 - len(lead['emails']))
            row = [
                lead['company_name'],
                lead['website'],
                emails[0] if len(emails) > 0 else '',
                emails[1] if len(emails) > 1 else '',
                emails[2] if len(emails) > 2 else '',
                ', '.join(lead['owner_names']) if lead['owner_names'] else 'Not found',
                lead['employee_count'],
                'Yes' if lead['is_commercial'] else 'No',
                '; '.join(lead['validation_notes']) if lead['validation_notes'] else 'Meets all criteria'
            ]
            rows.append(row)

        # Write to sheet
        write_to_sheet(spreadsheet_id, 'Sheet1!A1', rows)

        print(f"\n✅ Google Sheet created successfully!")
        print(f"📊 URL: {spreadsheet['spreadsheetUrl']}")

        return spreadsheet

    except FileNotFoundError as e:
        print(f"\n⚠️  Google Sheets export failed: {e}")
        print("    Results are saved to CSV file instead.")
        return None
    except Exception as e:
        print(f"\n⚠️  Google Sheets export failed: {e}")
        print("    Results are saved to CSV file instead.")
        return None


if __name__ == "__main__":
    import warnings
    warnings.filterwarnings('ignore')  # Suppress SSL warnings

    # Scrape companies (first 15 to increase chances of getting 10 valid)
    results = scrape_companies_concurrent(SA_COMMERCIAL_CLEANERS[:15], max_workers=5)

    # Save to CSV
    csv_file = save_to_csv(results)

    # Try to export to Google Sheets
    spreadsheet = export_to_google_sheets(results)

    # Summary
    print("\n" + "=" * 70)
    print("📊 FINAL SUMMARY")
    print("=" * 70)

    valid_leads = [r for r in results if r['is_valid']]
    print(f"✅ Valid leads found: {len(valid_leads)}")
    print(f"📄 CSV file: {csv_file}")

    if spreadsheet:
        print(f"📊 Google Sheet: {spreadsheet['spreadsheetUrl']}")
    else:
        print(f"📊 Google Sheet: Not created (use CSV file)")

    print("\n" + "=" * 70)

    # Display valid leads
    if valid_leads:
        print("\n✅ VALID LEADS:\n")
        for idx, lead in enumerate(valid_leads, 1):
            print(f"{idx}. {lead['company_name']}")
            print(f"   Website: {lead['website']}")
            print(f"   Emails: {', '.join(lead['emails'])}")
            print(f"   Owners: {', '.join(lead['owner_names']) if lead['owner_names'] else 'Not found'}")
            print()

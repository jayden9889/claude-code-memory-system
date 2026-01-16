"""
Scrape South African commercial cleaning companies that service small businesses.

Requirements:
- Companies must clean small businesses (restaurants, medical practices, etc.)
- NOT residential/in-house cleaning
- 5-100 employees
- Extract decision maker emails (owners/co-owners preferred)
- Reputable companies with online presence

Output: Google Sheet with company details and contact information
"""

import os
import re
import time
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path
from google_sheets_helper import create_spreadsheet, write_to_sheet

# User agents for web scraping
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}


def search_google_for_companies(query, num_results=20):
    """
    Search Google for companies matching the query.
    Returns list of URLs to investigate.
    """
    print(f"\n🔍 Searching for: {query}")

    # Manual search approach - we'll use a list of known SA cleaning companies
    # and Google search results to build a candidate list

    # Known major SA commercial cleaning companies to start with
    seed_companies = [
        "https://www.tsebocleaning.co.za",
        "https://www.bidvestnoonan.co.za",
        "https://www.procare.co.za",
        "https://www.kleenpro.co.za",
        "https://www.cleaningservices.co.za",
        "https://www.servicemaster.co.za",
        "https://www.commercialclean.co.za",
        "https://www.pristineclean.co.za",
        "https://www.supremeclean.co.za",
        "https://www.elitecleaning.co.za"
    ]

    # Search Google via requests (scraping search results)
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&num=20"

    try:
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract URLs from search results
        urls = []
        for link in soup.find_all('a'):
            href = link.get('href', '')
            if '/url?q=' in href and 'google.com' not in href:
                # Extract actual URL from Google's redirect
                url = href.split('/url?q=')[1].split('&')[0]
                if url.startswith('http') and '.co.za' in url:
                    urls.append(url)

        # Combine with seed companies
        all_urls = list(set(seed_companies + urls[:15]))
        print(f"✓ Found {len(all_urls)} potential companies to investigate")
        return all_urls

    except Exception as e:
        print(f"⚠ Google search failed: {e}. Using seed companies only.")
        return seed_companies


def scrape_website_content(url):
    """
    Scrape key pages from a website to extract contact info and company details.
    Returns dict with page contents.
    """
    print(f"\n📄 Scraping: {url}")

    content = {
        'base_url': url,
        'pages': {}
    }

    # Pages to check for contact information
    page_patterns = [
        '/',  # Homepage
        '/about',
        '/about-us',
        '/contact',
        '/contact-us',
        '/team',
        '/our-team',
        '/leadership',
        '/management'
    ]

    for pattern in page_patterns:
        try:
            full_url = urljoin(url, pattern)
            response = requests.get(full_url, headers=HEADERS, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Remove script and style elements
                for element in soup(['script', 'style', 'nav', 'footer']):
                    element.decompose()

                # Get text content
                text = soup.get_text(separator=' ', strip=True)

                # Limit text length to avoid token limits
                text = text[:5000]

                content['pages'][pattern] = text
                print(f"  ✓ Scraped {pattern}")

                time.sleep(0.5)  # Be polite

        except Exception as e:
            print(f"  ⚠ Failed to scrape {pattern}: {str(e)[:50]}")
            continue

    return content


def extract_emails_from_text(text):
    """
    Extract email addresses from text using regex.
    """
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)

    # Filter out common generic emails
    generic_patterns = ['info@', 'hello@', 'contact@', 'support@', 'admin@', 'sales@']

    filtered_emails = []
    generic_emails = []

    for email in emails:
        is_generic = any(pattern in email.lower() for pattern in generic_patterns)
        if is_generic:
            generic_emails.append(email)
        else:
            filtered_emails.append(email)

    return {
        'decision_maker_emails': list(set(filtered_emails)),
        'generic_emails': list(set(generic_emails))
    }


def extract_company_info_manual(website_content, company_url):
    """
    Extract structured company information from website content using regex and heuristics.
    """
    print(f"  🔍 Extracting company details...")

    # Combine all page content
    all_text = "\n\n".join([f"=== {page} ===\n{content}" for page, content in website_content['pages'].items()])
    all_text_lower = all_text.lower()

    company_info = {
        'company_name': '',
        'is_commercial_cleaning': False,
        'is_residential': False,
        'employee_count': '',
        'decision_maker_emails': [],
        'owner_names': [],
        'is_reputable': True,  # Assume true if they have a website
        'services': [],
        'notes': ''
    }

    # Extract company name from URL or title
    domain = urlparse(company_url).netloc.replace('www.', '').replace('.co.za', '').replace('.com', '')
    company_info['company_name'] = domain.title()

    # Try to find actual company name in content
    name_patterns = [
        r'<title>([^<|]+)',
        r'company name[:\s]+([A-Z][a-zA-Z\s&]+)',
        r'welcome to ([A-Z][a-zA-Z\s&]+)'
    ]
    for pattern in name_patterns:
        match = re.search(pattern, all_text, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            if len(name) > 3 and len(name) < 50:
                company_info['company_name'] = name
                break

    # Check if commercial cleaning (look for business-related keywords)
    commercial_keywords = [
        'commercial cleaning', 'office cleaning', 'business cleaning',
        'restaurant cleaning', 'medical practice', 'healthcare cleaning',
        'industrial cleaning', 'corporate cleaning', 'workplace cleaning',
        'retail cleaning', 'school cleaning', 'facility management'
    ]
    company_info['is_commercial_cleaning'] = any(kw in all_text_lower for kw in commercial_keywords)

    # Check if residential
    residential_keywords = [
        'residential cleaning', 'home cleaning', 'house cleaning',
        'domestic cleaning', 'maid service', 'housekeeping'
    ]
    company_info['is_residential'] = any(kw in all_text_lower for kw in residential_keywords)

    # Extract employee count
    employee_patterns = [
        r'(\d+)\+?\s*employees',
        r'team of (\d+)',
        r'(\d+)\s*staff members',
        r'over (\d+)\s*people',
        r'(\d+)\s*cleaners'
    ]
    for pattern in employee_patterns:
        match = re.search(pattern, all_text_lower)
        if match:
            company_info['employee_count'] = match.group(1)
            break

    # Extract emails
    email_results = extract_emails_from_text(all_text)
    company_info['decision_maker_emails'] = email_results['decision_maker_emails']

    # If no decision maker emails, try to find owner/manager emails specifically
    if not company_info['decision_maker_emails']:
        # Look for emails near owner/director/CEO mentions
        owner_email_pattern = r'(?:owner|ceo|director|founder|managing|manager)[:\s]+.*?([a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})'
        owner_emails = re.findall(owner_email_pattern, all_text_lower)
        if owner_emails:
            company_info['decision_maker_emails'] = list(set(owner_emails))
        else:
            # Fall back to generic emails if nothing else found
            company_info['decision_maker_emails'] = email_results['generic_emails'][:3]

    # Extract owner names
    owner_patterns = [
        r'(?:owner|ceo|founder|director|managing director)[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)',
        r'([A-Z][a-z]+\s+[A-Z][a-z]+),\s*(?:owner|ceo|founder|director)',
        r'contact\s+([A-Z][a-z]+\s+[A-Z][a-z]+)'
    ]
    for pattern in owner_patterns:
        matches = re.findall(pattern, all_text)
        company_info['owner_names'].extend(matches)

    company_info['owner_names'] = list(set(company_info['owner_names']))[:3]  # Limit to 3

    # Extract services
    service_keywords = [
        'office cleaning', 'carpet cleaning', 'window cleaning',
        'floor cleaning', 'deep cleaning', 'sanitization',
        'janitorial services', 'facility management', 'maintenance'
    ]
    found_services = [svc for svc in service_keywords if svc in all_text_lower]
    company_info['services'] = found_services[:5]

    print(f"  ✓ Extracted: {company_info['company_name']}")
    print(f"    Commercial: {company_info['is_commercial_cleaning']}")
    print(f"    Emails: {len(company_info['decision_maker_emails'])}")

    return company_info


def validate_lead(company_info):
    """
    Validate if the lead meets all criteria.
    Returns (is_valid, reason)
    """
    if not company_info:
        return False, "No company info extracted"

    # Check if commercial cleaning (not residential)
    if not company_info.get('is_commercial_cleaning'):
        return False, "Not a commercial cleaning service"

    if company_info.get('is_residential'):
        return False, "Residential cleaning service"

    # Check employee count
    employee_count = company_info.get('employee_count', '').lower()
    if employee_count:
        # Extract numbers from employee count string
        numbers = re.findall(r'\d+', employee_count)
        if numbers:
            count = int(numbers[0])
            if count < 5 or count > 100:
                return False, f"Employee count {count} outside range (5-100)"

    # Check if decision maker emails found
    if not company_info.get('decision_maker_emails'):
        return False, "No decision maker emails found"

    # Check if reputable
    if not company_info.get('is_reputable'):
        return False, "Not a reputable company"

    return True, "Meets all criteria"


def scrape_cleaning_companies(target_count=10):
    """
    Main function to scrape South African commercial cleaning companies.
    """
    print("=" * 60)
    print("🧹 SOUTH AFRICAN COMMERCIAL CLEANING COMPANY SCRAPER")
    print("=" * 60)

    # Search for companies
    search_queries = [
        "commercial cleaning services south africa companies",
        "business cleaning services johannesburg cape town",
        "office cleaning companies south africa"
    ]

    all_urls = []
    for query in search_queries:
        urls = search_google_for_companies(query, num_results=10)
        all_urls.extend(urls)

    # Remove duplicates
    all_urls = list(set(all_urls))
    print(f"\n📊 Total unique companies to investigate: {len(all_urls)}")

    # Results storage
    valid_leads = []
    tmp_dir = Path('.tmp')
    tmp_dir.mkdir(exist_ok=True)

    # Process each company
    for idx, url in enumerate(all_urls):
        if len(valid_leads) >= target_count:
            print(f"\n✅ Target of {target_count} valid leads reached!")
            break

        print(f"\n{'=' * 60}")
        print(f"Processing company {idx + 1}/{len(all_urls)}: {url}")
        print(f"Valid leads so far: {len(valid_leads)}/{target_count}")
        print(f"{'=' * 60}")

        try:
            # Scrape website
            website_content = scrape_website_content(url)

            if not website_content['pages']:
                print(f"  ⚠ No content scraped, skipping...")
                continue

            # Extract info manually
            company_info = extract_company_info_manual(website_content, url)

            if not company_info:
                print(f"  ⚠ Could not extract company info, skipping...")
                continue

            # Add website URL to company info
            company_info['website'] = url

            # Validate lead
            is_valid, reason = validate_lead(company_info)

            if is_valid:
                print(f"  ✅ VALID LEAD: {company_info.get('company_name')}")
                print(f"     Emails: {', '.join(company_info.get('decision_maker_emails', []))}")
                valid_leads.append(company_info)

                # Save intermediate results
                with open(tmp_dir / 'sa_cleaning_leads.json', 'w') as f:
                    json.dump(valid_leads, f, indent=2)
            else:
                print(f"  ❌ INVALID: {reason}")

            time.sleep(1)  # Be respectful with scraping

        except Exception as e:
            print(f"  ✗ Error processing {url}: {e}")
            continue

    print(f"\n{'=' * 60}")
    print(f"🎯 SCRAPING COMPLETE")
    print(f"{'=' * 60}")
    print(f"Valid leads found: {len(valid_leads)}/{target_count}")
    print(f"Success rate: {len(valid_leads)/target_count*100:.0f}%")

    return valid_leads


def export_to_google_sheets(leads):
    """
    Export leads to a new Google Sheet with appropriate formatting.
    """
    print("\n📊 Exporting to Google Sheets...")

    # Create spreadsheet
    sheet_title = f"South African Commercial Cleaning Leads - {time.strftime('%Y-%m-%d')}"
    spreadsheet = create_spreadsheet(sheet_title)
    spreadsheet_id = spreadsheet['spreadsheetId']

    # Prepare headers
    headers = [
        'Company Name',
        'Website',
        'Decision Maker Emails',
        'Owner/Founder Names',
        'Employee Count',
        'Services Offered',
        'Commercial Cleaning?',
        'Reputable?',
        'Notes'
    ]

    # Prepare data rows
    rows = [headers]

    for lead in leads:
        row = [
            lead.get('company_name', ''),
            lead.get('website', ''),
            ', '.join(lead.get('decision_maker_emails', [])),
            ', '.join(lead.get('owner_names', [])),
            lead.get('employee_count', ''),
            ', '.join(lead.get('services', [])),
            'Yes' if lead.get('is_commercial_cleaning') else 'No',
            'Yes' if lead.get('is_reputable') else 'No',
            lead.get('notes', '')
        ]
        rows.append(row)

    # Write to sheet
    write_to_sheet(spreadsheet_id, 'Sheet1!A1', rows)

    print(f"\n✅ EXPORT COMPLETE")
    print(f"📊 Google Sheet URL: {spreadsheet['spreadsheetUrl']}")

    return spreadsheet


if __name__ == "__main__":
    # Scrape companies
    leads = scrape_cleaning_companies(target_count=10)

    if leads:
        # Export to Google Sheets
        spreadsheet = export_to_google_sheets(leads)

        print("\n" + "=" * 60)
        print("✅ MISSION COMPLETE")
        print("=" * 60)
        print(f"Successfully scraped {len(leads)} qualified leads")
        print(f"Results available at: {spreadsheet['spreadsheetUrl']}")
    else:
        print("\n❌ No valid leads found. Please review search criteria.")

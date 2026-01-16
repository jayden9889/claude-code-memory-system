#!/usr/bin/env python3
"""
Verify each company is B2B cleaning focused and try to find decision-maker emails.
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import warnings
warnings.filterwarnings('ignore')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

COMPANIES = [
    {'name': 'Bidvest Prestige Cleaning', 'website': 'https://www.bidvestprestige.co.za'},
    {'name': 'ServiceMaster SA', 'website': 'https://www.servicemaster.co.za'},
    {'name': 'Procare Commercial Cleaning', 'website': 'https://www.procare.co.za'},
    {'name': 'CleanCo Johannesburg', 'website': 'https://www.cleanco.co.za'},
    {'name': 'Bee Clean Commercial', 'website': 'https://www.beeclean.co.za'},
    {'name': 'Absolute Cleaning Services', 'website': 'https://absolutecleaning.co.za'},
    {'name': 'Crystal Clear Commercial', 'website': 'https://crystalclear.co.za'},
    {'name': 'Initial Hygiene South Africa', 'website': 'https://www.initial.co.za'},
    {'name': 'Tsebo Solutions', 'website': 'https://www.tsebo.com'},
    {'name': 'A-Len Cleaning Services', 'website': 'https://www.alen.co.za'}
]

def deep_scrape_company(url):
    """Scrape company website for B2B indicators and decision-maker info."""
    try:
        pages = ['/', '/about', '/about-us', '/services', '/contact', '/team', '/leadership']
        all_text = ""
        all_emails = []
        
        for page in pages:
            try:
                full_url = url.rstrip('/') + page
                response = requests.get(full_url, headers=HEADERS, timeout=10, verify=False, allow_redirects=True)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Remove scripts, styles
                    for elem in soup(['script', 'style', 'nav', 'footer']):
                        elem.decompose()
                    
                    text = soup.get_text(separator=' ', strip=True)
                    all_text += " " + text.lower()
                    
                    # Extract emails
                    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                    emails = re.findall(email_pattern, response.text)
                    all_emails.extend(emails)
                
                time.sleep(0.5)
            except:
                continue
        
        # Check if B2B cleaning
        b2b_keywords = [
            'commercial cleaning', 'office cleaning', 'business cleaning',
            'corporate cleaning', 'workplace cleaning', 'facility cleaning',
            'industrial cleaning', 'retail cleaning', 'restaurant cleaning',
            'medical facility', 'healthcare cleaning', 'school cleaning',
            'b2b', 'business to business', 'commercial clients', 'corporate clients'
        ]
        
        residential_keywords = [
            'home cleaning', 'residential cleaning', 'house cleaning',
            'domestic cleaning', 'maid service'
        ]
        
        waste_keywords = [
            'waste management', 'waste removal', 'refuse collection',
            'garbage collection', 'trash removal', 'skip hire'
        ]
        
        is_b2b = any(kw in all_text for kw in b2b_keywords)
        is_residential = any(kw in all_text for kw in residential_keywords)
        is_waste = any(kw in all_text for kw in waste_keywords)
        
        # Find decision-maker emails
        all_emails = list(set(all_emails))
        
        # Categorize emails
        decision_maker_patterns = [
            'ceo@', 'director@', 'owner@', 'founder@', 'managing@',
            'md@', 'gm@', 'manager@', 'operations@', 'sales@'
        ]
        
        generic_patterns = [
            'info@', 'contact@', 'hello@', 'support@', 'admin@',
            'enquiries@', 'reception@', 'office@'
        ]
        
        decision_maker_emails = [e for e in all_emails if any(p in e.lower() for p in decision_maker_patterns)]
        generic_emails = [e for e in all_emails if any(p in e.lower() for p in generic_patterns)]
        other_emails = [e for e in all_emails if e not in decision_maker_emails and e not in generic_emails]
        
        return {
            'is_b2b': is_b2b,
            'is_residential_only': is_residential and not is_b2b,
            'is_waste': is_waste,
            'decision_maker_emails': decision_maker_emails[:3],
            'other_emails': other_emails[:3],
            'generic_emails': generic_emails[:2],
            'content_snippet': all_text[:500]
        }
        
    except Exception as e:
        return {'error': str(e)}

if __name__ == "__main__":
    print("=" * 80)
    print("🔍 DEEP VERIFICATION: B2B STATUS & DECISION-MAKER EMAILS")
    print("=" * 80)
    print()
    
    results = []
    
    for idx, company in enumerate(COMPANIES, 1):
        print(f"{idx}. {company['name']}")
        print(f"   Website: {company['website']}")
        
        result = deep_scrape_company(company['website'])
        
        if 'error' in result:
            print(f"   ⚠️  Could not scrape: {result['error']}")
            results.append({
                'company': company['name'],
                'b2b_verified': 'Unknown',
                'emails': 'Could not verify'
            })
        else:
            # B2B Status
            if result['is_b2b'] and not result['is_waste']:
                print(f"   ✅ CONFIRMED B2B CLEANING")
                b2b_status = "✅ B2B Cleaning"
            elif result['is_residential_only']:
                print(f"   ❌ RESIDENTIAL ONLY (not B2B)")
                b2b_status = "❌ Residential Only"
            elif result['is_waste']:
                print(f"   ❌ WASTE MANAGEMENT (not cleaning)")
                b2b_status = "❌ Waste Management"
            else:
                print(f"   ⚠️  Could not confirm B2B status")
                b2b_status = "⚠️ Unconfirmed"
            
            # Decision-maker emails
            if result['decision_maker_emails']:
                print(f"   👔 Decision-maker emails: {', '.join(result['decision_maker_emails'])}")
                email_status = f"Decision-maker: {', '.join(result['decision_maker_emails'])}"
            elif result['other_emails']:
                print(f"   📧 Other emails: {', '.join(result['other_emails'])}")
                email_status = f"Other: {', '.join(result['other_emails'])}"
            elif result['generic_emails']:
                print(f"   📧 Generic emails: {', '.join(result['generic_emails'])}")
                email_status = f"Generic: {', '.join(result['generic_emails'])}"
            else:
                print(f"   ⚠️  No emails found")
                email_status = "No emails found"
            
            results.append({
                'company': company['name'],
                'b2b_verified': b2b_status,
                'emails': email_status
            })
        
        print()
        time.sleep(1)
    
    # Summary
    print("=" * 80)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 80)
    print()
    
    b2b_count = sum(1 for r in results if '✅' in r['b2b_verified'])
    decision_maker_count = sum(1 for r in results if 'Decision-maker' in r['emails'])
    
    print(f"✅ Confirmed B2B cleaning: {b2b_count}/10")
    print(f"👔 Decision-maker emails found: {decision_maker_count}/10")
    print()
    
    for r in results:
        print(f"• {r['company']}")
        print(f"  B2B Status: {r['b2b_verified']}")
        print(f"  Emails: {r['emails']}")
        print()

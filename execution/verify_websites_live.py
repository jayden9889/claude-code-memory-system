#!/usr/bin/env python3
"""
Verify that all websites in our leads are actually live and accessible.
"""

import requests
import csv
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

def test_website(url, timeout=10):
    """Test if a website is live and accessible."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout, verify=False, allow_redirects=True)
        if response.status_code == 200:
            return True, response.url, response.status_code
        else:
            return False, None, response.status_code
    except requests.exceptions.Timeout:
        return False, None, "Timeout"
    except requests.exceptions.ConnectionError:
        return False, None, "Connection Error"
    except Exception as e:
        return False, None, str(e)

if __name__ == "__main__":
    print("=" * 70)
    print("🔍 VERIFYING WEBSITE ACCESSIBILITY")
    print("=" * 70)
    print()
    
    # Read the CSV
    csv_path = Path('.tmp/verified_sa_cleaning_leads.csv')
    
    if not csv_path.exists():
        print(f"❌ CSV file not found: {csv_path}")
        exit(1)
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        leads = list(reader)
    
    print(f"📋 Testing {len(leads)} websites...\n")
    
    working_count = 0
    failed_count = 0
    
    for idx, lead in enumerate(leads, 1):
        company = lead['Company Name']
        website = lead['Website']
        
        print(f"{idx}. {company}")
        print(f"   URL: {website}")
        
        is_live, final_url, status = test_website(website)
        
        if is_live:
            print(f"   ✅ LIVE (Status: {status})")
            if final_url != website:
                print(f"   ↪️  Redirects to: {final_url}")
            working_count += 1
        else:
            print(f"   ❌ FAILED (Status: {status})")
            failed_count += 1
        
        print()
    
    print("=" * 70)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 70)
    print(f"✅ Working websites: {working_count}/{len(leads)}")
    print(f"❌ Failed websites: {failed_count}/{len(leads)}")
    print(f"📈 Success rate: {(working_count/len(leads)*100):.1f}%")
    print()
    
    if working_count == len(leads):
        print("🎉 All websites are live and accessible!")
    elif working_count >= len(leads) * 0.8:
        print("✅ Most websites are working (80%+ success rate)")
    else:
        print("⚠️  Many websites are not accessible - may need manual verification")

#!/usr/bin/env python3
"""
Create Instantly email campaigns with A/B testing.
Creates split-test campaigns for B2B cleaning lead generation offer.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

INSTANTLY_API_KEY = os.getenv('INSTANTLY_API_KEY')
# v2 API uses Bearer token auth
INSTANTLY_API_BASE = 'https://api.instantly.ai/api/v2'


def create_campaign(name: str, sequences: list, sending_account: str = None) -> dict:
    """
    Create a campaign in Instantly.

    Args:
        name: Campaign name
        sequences: List of sequence steps with variants
        sending_account: Email address to send from (optional)

    Returns:
        API response dict
    """
    if not INSTANTLY_API_KEY:
        raise ValueError("INSTANTLY_API_KEY not found in environment variables")

    # v2 API uses Bearer token authentication
    headers = {
        'Authorization': f'Bearer {INSTANTLY_API_KEY}',
        'Content-Type': 'application/json'
    }

    # v2 API uses numeric day keys: 0=Sunday, 1=Monday, etc.
    payload = {
        "name": name,
        "sequences": sequences,
        "campaign_schedule": {
            "schedules": [{
                "name": "Weekday Schedule",
                "days": {
                    "1": True,  # Monday
                    "2": True,  # Tuesday
                    "3": True,  # Wednesday
                    "4": True,  # Thursday
                    "5": True   # Friday
                },
                "timing": {"from": "09:00", "to": "17:00"},
                "timezone": "America/Chicago"
            }]
        },
        "daily_limit": 50,
        "stop_on_reply": True,
        "stop_on_auto_reply": True,
        "link_tracking": True,
        "open_tracking": True
    }

    response = requests.post(
        f'{INSTANTLY_API_BASE}/campaigns',
        headers=headers,
        json=payload
    )

    if response.status_code not in [200, 201]:
        print(f"Error creating campaign: {response.status_code}")
        print(f"Response: {response.text}")
        response.raise_for_status()

    return response.json()


def add_leads_to_campaign(campaign_id: str, leads: list) -> dict:
    """
    Add leads to an Instantly campaign.

    Args:
        campaign_id: The campaign ID
        leads: List of lead dicts with email, firstName, companyName, etc.

    Returns:
        API response dict
    """
    if not INSTANTLY_API_KEY:
        raise ValueError("INSTANTLY_API_KEY not found in environment variables")

    headers = {
        'Authorization': f'Bearer {INSTANTLY_API_KEY}',
        'Content-Type': 'application/json'
    }

    # Convert leads to Instantly's expected format (snake_case)
    formatted_leads = []
    for lead in leads:
        formatted_lead = {
            "email": lead.get("email"),
            "first_name": lead.get("firstName", ""),
            "last_name": lead.get("lastName", ""),
            "company_name": lead.get("companyName", ""),
            # Custom variables for personalization
            "custom_variables": {
                "casualCompanyName": lead.get("casualCompanyName", ""),
                "icebreaker": lead.get("icebreaker", "")
            }
        }
        formatted_leads.append(formatted_lead)

    payload = {
        "campaign_id": campaign_id,
        "leads": formatted_leads
    }

    response = requests.post(
        f'{INSTANTLY_API_BASE}/leads/add',
        headers=headers,
        json=payload
    )

    if response.status_code not in [200, 201]:
        print(f"Error adding leads: {response.status_code}")
        print(f"Response: {response.text}")
        response.raise_for_status()

    return response.json()


def text_to_html(text: str) -> str:
    """Convert plain text to HTML paragraphs."""
    paragraphs = text.strip().split('\n\n')
    html_parts = []
    for p in paragraphs:
        # Handle single line breaks within paragraphs
        p = p.replace('\n', '<br>')
        html_parts.append(f'<p>{p}</p>')
    return ''.join(html_parts)


# ============================================================
# EMAIL TEMPLATES - B2B CLEANING LEAD GENERATION
# ============================================================

# Variant A: Results-Focused / Direct
VARIANT_A_SUBJECT = "{{firstName}}, quick question"
VARIANT_A_BODY = """{{firstName}},

{{icebreaker}}

I know this is out of left field, but I work specifically with commercial cleaning companies in South Africa.

Basically, I fill your pipeline with pre-qualified B2B leads - businesses actively looking for cleaning services. We're talking 30-50+ qualified leads per month.

No fluff. No tire-kickers. Just decision makers who need cleaning services.

Here's my offer: I'll get you 30 qualified leads in the next 30 days or you don't pay a thing. I'd handle everything, you just close the deals.

Would this be of value to {{casualCompanyName}} at all? If so, happy to send over a quick video explaining how it works.

Thanks,
{{sendingAccountFirstName}}"""

# Variant B: Problem-Aware / Consultative
VARIANT_B_SUBJECT = "{{firstName}} - filling your pipeline"
VARIANT_B_BODY = """{{firstName}},

{{icebreaker}}

Quick question - is {{casualCompanyName}} actively looking to take on more commercial cleaning contracts?

If so, I might be able to help. I work with cleaning companies to fill their pipeline with pre-qualified B2B leads. Businesses that are actively searching for cleaning services.

Most of my clients see 30-50+ new qualified opportunities hitting their inbox every month.

The best part? I guarantee results. If I don't deliver 30+ qualified leads in 30 days, you pay nothing.

Worth a 5-minute call to see if this could work for {{casualCompanyName}}?

Best,
{{sendingAccountFirstName}}"""

# Follow-up email (Step 2)
FOLLOWUP_SUBJECT = "Re: {{firstName}}, quick question"
FOLLOWUP_BODY = """{{firstName}},

Just bumping this up in case it got buried.

I know commercial cleaning is competitive - that's exactly why consistent lead flow matters.

Would it be worth a quick chat to see if we could help {{casualCompanyName}} book more contracts?

{{sendingAccountFirstName}}"""

# Breakup email (Step 3)
BREAKUP_SUBJECT = "Re: {{firstName}}, quick question"
BREAKUP_BODY = """{{firstName}},

I'll keep this short - I've reached out a couple times about helping {{casualCompanyName}} get more cleaning contracts.

If the timing isn't right, no worries at all. But if you ever want 30-50+ qualified B2B leads landing in your inbox monthly, just reply and we can chat.

Either way, wishing you success.

{{sendingAccountFirstName}}"""


def get_b2b_cleaning_campaign_sequences():
    """
    Build the campaign sequences for B2B cleaning lead gen.
    Returns sequence structure for Instantly API.
    """
    return [{
        "steps": [
            {
                "type": "email",
                "delay": 0,
                "variants": [
                    {
                        "subject": VARIANT_A_SUBJECT,
                        "body": text_to_html(VARIANT_A_BODY)
                    },
                    {
                        "subject": VARIANT_B_SUBJECT,
                        "body": text_to_html(VARIANT_B_BODY)
                    }
                ]
            },
            {
                "type": "email",
                "delay": 3,  # 3 days after first email
                "variants": [{
                    "subject": FOLLOWUP_SUBJECT,
                    "body": text_to_html(FOLLOWUP_BODY)
                }]
            },
            {
                "type": "email",
                "delay": 4,  # 4 days after follow-up (7 total)
                "variants": [{
                    "subject": BREAKUP_SUBJECT,
                    "body": text_to_html(BREAKUP_BODY)
                }]
            }
        ]
    }]


def get_cleaning_leads_with_icebreakers():
    """
    Get the 10 B2B cleaning leads with personalized icebreakers.
    Returns list of lead dicts ready for Instantly.
    """
    leads = [
        {
            "email": "info@bidvestprestige.co.za",
            "firstName": "Team",
            "lastName": "",
            "companyName": "Bidvest Prestige Cleaning",
            "casualCompanyName": "Bidvest Prestige",
            "icebreaker": "Saw that Bidvest Prestige has grown to 23,000+ employees and achieved B-BBEE Level 1 certification - impressive scale in the SA cleaning market."
        },
        {
            "email": "customercare@servicemaster.co.za",
            "firstName": "Team",
            "lastName": "",
            "companyName": "ServiceMaster SA",
            "casualCompanyName": "ServiceMaster",
            "icebreaker": "56 years in the industry with 14+ branches across South Africa - that kind of longevity speaks volumes about your reputation."
        },
        {
            "email": "info@procare.co.za",
            "firstName": "Team",
            "lastName": "",
            "companyName": "Procare Commercial Cleaning",
            "casualCompanyName": "Procare",
            "icebreaker": "Noticed Procare has become a leader in Gauteng commercial cleaning - always good to see local companies dominating their market."
        },
        {
            "email": "info@cleanco.co.za",
            "firstName": "Team",
            "lastName": "",
            "companyName": "CleanCo Johannesburg",
            "casualCompanyName": "CleanCo",
            "icebreaker": "Multi-city operations take serious coordination - CleanCo clearly knows how to scale commercial cleaning."
        },
        {
            "email": "info@beeclean.co.za",
            "firstName": "Team",
            "lastName": "",
            "companyName": "Bee Clean Commercial",
            "casualCompanyName": "Bee Clean",
            "icebreaker": "Love that Bee Clean has achieved Level 1 B-BBEE status and focuses on staff development as your key differentiator - that's how you build a lasting business."
        },
        {
            "email": "kathy@absolutecleaning.co.za",
            "firstName": "Kathy",
            "lastName": "",
            "companyName": "Absolute Cleaning Services",
            "casualCompanyName": "Absolute Cleaning",
            "icebreaker": "Saw Absolute Cleaning is based in Edenvale and focuses on essential hygiene solutions - solid niche in the Johannesburg market."
        },
        {
            "email": "info@crystalclear.co.za",
            "firstName": "Team",
            "lastName": "",
            "companyName": "Crystal Clear Commercial",
            "casualCompanyName": "Crystal Clear",
            "icebreaker": "Cape Town's commercial cleaning scene is competitive - Crystal Clear has clearly carved out a strong position."
        },
        {
            "email": "info@initial.co.za",
            "firstName": "Team",
            "lastName": "",
            "companyName": "Initial Hygiene South Africa",
            "casualCompanyName": "Initial Hygiene",
            "icebreaker": "Being part of the Rentokil Initial group gives you serious credibility in the SA hygiene market - that global backing is a major advantage."
        },
        {
            "email": "info@tsebo.com",
            "firstName": "Team",
            "lastName": "",
            "companyName": "Tsebo Solutions",
            "casualCompanyName": "Tsebo",
            "icebreaker": "Congrats on the Top Employer Africa 2025 recognition - 50+ years in facilities management and you're still leading the pack."
        },
        {
            "email": "info@alen.co.za",
            "firstName": "Team",
            "lastName": "",
            "companyName": "A-Len Cleaning Services",
            "casualCompanyName": "A-Len",
            "icebreaker": "BEE Level 1 with large corporate contracts - A-Len has clearly built the trust needed to win big in industrial cleaning."
        },
        # Test lead - Jayden's personal email
        {
            "email": "jaydenmortimer.9@gmail.com",
            "firstName": "Jayden",
            "lastName": "Mortimer",
            "companyName": "Test Company (Your Preview)",
            "casualCompanyName": "Test Company",
            "icebreaker": "This is a test email so you can see exactly what your leads will receive - pretty cool right?"
        }
    ]

    return leads


def preview_emails():
    """Preview the email templates with sample data."""
    sample_lead = {
        "firstName": "John",
        "casualCompanyName": "ABC Cleaning",
        "sendingAccountFirstName": "Jayden"
    }

    print("\n" + "=" * 70)
    print("EMAIL PREVIEW - VARIANT A (Results-Focused)")
    print("=" * 70)
    print(f"\nSubject: {VARIANT_A_SUBJECT}")
    print(f"\nBody:\n{VARIANT_A_BODY}")

    print("\n" + "=" * 70)
    print("EMAIL PREVIEW - VARIANT B (Consultative)")
    print("=" * 70)
    print(f"\nSubject: {VARIANT_B_SUBJECT}")
    print(f"\nBody:\n{VARIANT_B_BODY}")

    print("\n" + "=" * 70)
    print("FOLLOW-UP EMAIL (Step 2)")
    print("=" * 70)
    print(f"\nSubject: {FOLLOWUP_SUBJECT}")
    print(f"\nBody:\n{FOLLOWUP_BODY}")

    print("\n" + "=" * 70)
    print("BREAKUP EMAIL (Step 3)")
    print("=" * 70)
    print(f"\nSubject: {BREAKUP_SUBJECT}")
    print(f"\nBody:\n{BREAKUP_BODY}")


def export_campaign_json(dry_run=True):
    """
    Export the campaign payload as JSON for manual review or API upload.

    Args:
        dry_run: If True, just export JSON. If False, create in Instantly.
    """
    campaign_name = "B2B Cleaning | Lead Gen Offer | Split Test"
    sequences = get_b2b_cleaning_campaign_sequences()
    leads = get_cleaning_leads_with_icebreakers()

    # Calculate dates
    start_date = datetime.now().strftime('%Y-%m-%d')
    end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')

    campaign_payload = {
        "name": campaign_name,
        "sequences": sequences,
        "campaign_schedule": {
            "schedules": [{
                "name": "Weekday Schedule",
                "days": {
                    "1": True,  # Monday
                    "2": True,  # Tuesday
                    "3": True,  # Wednesday
                    "4": True,  # Thursday
                    "5": True   # Friday
                },
                "timing": {"from": "09:00", "to": "17:00"},
                "timezone": "America/Chicago"
            }]
        },
        "daily_limit": 50,
        "stop_on_reply": True,
        "stop_on_auto_reply": True,
        "link_tracking": True,
        "open_tracking": True
    }

    # Export to .tmp folder
    tmp_dir = Path('.tmp')
    tmp_dir.mkdir(exist_ok=True)

    # Save campaign payload
    campaign_file = tmp_dir / 'instantly_campaign_payload.json'
    with open(campaign_file, 'w') as f:
        json.dump(campaign_payload, f, indent=2)
    print(f"✓ Campaign payload saved to: {campaign_file}")

    # Save leads
    leads_file = tmp_dir / 'instantly_campaign_leads.json'
    with open(leads_file, 'w') as f:
        json.dump(leads, f, indent=2)
    print(f"✓ Leads saved to: {leads_file}")

    if dry_run:
        print("\n" + "=" * 70)
        print("DRY RUN COMPLETE")
        print("=" * 70)
        print("\nTo create the campaign in Instantly:")
        print("1. Add INSTANTLY_API_KEY to your .env file")
        print("2. Run: python execution/instantly_create_campaign.py --live")
        print("\nOr manually import the JSON files into Instantly.")
    else:
        if not INSTANTLY_API_KEY:
            print("\n❌ INSTANTLY_API_KEY not found in .env file!")
            print("Add it and run again with --live flag.")
            return None

        print("\n📤 Creating campaign in Instantly...")
        try:
            result = create_campaign(campaign_name, sequences)
            campaign_id = result.get('id')
            print(f"✓ Campaign created! ID: {campaign_id}")

            print("\n📤 Adding leads to campaign...")
            add_leads_to_campaign(campaign_id, leads)
            print(f"✓ Added {len(leads)} leads to campaign")

            print("\n" + "=" * 70)
            print("✅ CAMPAIGN CREATED SUCCESSFULLY!")
            print("=" * 70)
            print(f"\nCampaign: {campaign_name}")
            print(f"Leads: {len(leads)} (including your test email)")
            print("\nNext steps:")
            print("1. Go to Instantly dashboard")
            print("2. Review the campaign emails")
            print("3. Add sending account (jayden@mortaihq.com)")
            print("4. Start the campaign when ready")

            return result
        except Exception as e:
            print(f"\n❌ Error creating campaign: {e}")
            return None


def main():
    import sys

    print("=" * 70)
    print("INSTANTLY CAMPAIGN CREATOR - B2B CLEANING LEAD GEN")
    print("=" * 70)

    # Check for flags
    live_mode = '--live' in sys.argv
    preview_mode = '--preview' in sys.argv

    if preview_mode:
        preview_emails()
        return

    print("\n📋 Campaign Details:")
    print("   Target: B2B Cleaning Companies (South Africa)")
    print("   Offer: 30-50+ qualified leads per month")
    print("   A/B Test: 2 email variants")
    print("   Sending from: jayden@mortaihq.com")
    print("   Test email: jaydenmortimer.9@gmail.com")

    print("\n📧 Email Sequence:")
    print("   Step 1: Initial email (2 A/B variants)")
    print("   Step 2: Follow-up (3 days later)")
    print("   Step 3: Breakup email (7 days total)")

    leads = get_cleaning_leads_with_icebreakers()
    print(f"\n👥 Leads: {len(leads)} total (10 companies + 1 test)")

    export_campaign_json(dry_run=not live_mode)


if __name__ == "__main__":
    main()

"""
Validate and clean lead data.
Removes duplicates, validates emails, and enriches data.
"""

import sys
from utils import (
    load_json,
    save_json,
    validate_email,
    log_error,
    log_success
)


class LeadValidator:
    """Validate and clean lead data."""

    def __init__(self):
        """Initialize validator."""
        self.seen_emails = set()
        self.stats = {
            'total': 0,
            'valid': 0,
            'invalid_email': 0,
            'duplicate': 0,
            'missing_required': 0
        }

    def is_valid_lead(self, lead):
        """
        Check if a lead has all required fields and valid email.

        Args:
            lead (dict): Lead data

        Returns:
            tuple: (is_valid, reason)
        """
        # Check required fields
        required_fields = ['first_name', 'email', 'company_name']
        for field in required_fields:
            if not lead.get(field):
                return False, f"Missing required field: {field}"

        # Validate email
        email = lead.get('email', '').strip().lower()
        if not validate_email(email):
            return False, "Invalid email format"

        # Check for duplicates
        if email in self.seen_emails:
            return False, "Duplicate email"

        return True, "Valid"

    def clean_lead(self, lead):
        """
        Clean and normalize lead data.

        Args:
            lead (dict): Raw lead data

        Returns:
            dict: Cleaned lead data
        """
        cleaned = {}

        # Clean and normalize each field
        cleaned['first_name'] = lead.get('first_name', '').strip()
        cleaned['last_name'] = lead.get('last_name', '').strip()
        cleaned['email'] = lead.get('email', '').strip().lower()
        cleaned['title'] = lead.get('title', '').strip()
        cleaned['linkedin_url'] = lead.get('linkedin_url', '').strip()
        cleaned['company_name'] = lead.get('company_name', '').strip()
        cleaned['company_domain'] = lead.get('company_domain', '').strip().lower()
        cleaned['company_industry'] = lead.get('company_industry', '').strip()
        cleaned['company_size'] = lead.get('company_size', '')
        cleaned['city'] = lead.get('city', '').strip()
        cleaned['state'] = lead.get('state', '').strip()
        cleaned['country'] = lead.get('country', '').strip()

        # Add validation status
        cleaned['validation_status'] = 'valid'

        return cleaned

    def validate_leads(self, leads):
        """
        Validate a list of leads.

        Args:
            leads (list): List of lead dictionaries

        Returns:
            dict: Validation results with valid and invalid leads
        """
        valid_leads = []
        invalid_leads = []

        self.stats['total'] = len(leads)

        for lead in leads:
            is_valid, reason = self.is_valid_lead(lead)

            if is_valid:
                # Clean the lead
                cleaned_lead = self.clean_lead(lead)
                valid_leads.append(cleaned_lead)

                # Mark email as seen
                self.seen_emails.add(cleaned_lead['email'])
                self.stats['valid'] += 1

            else:
                # Track why it was invalid
                lead['invalid_reason'] = reason
                invalid_leads.append(lead)

                # Update stats
                if 'email' in reason.lower():
                    self.stats['invalid_email'] += 1
                elif 'duplicate' in reason.lower():
                    self.stats['duplicate'] += 1
                else:
                    self.stats['missing_required'] += 1

        return {
            'valid': valid_leads,
            'invalid': invalid_leads,
            'stats': self.stats
        }


def main(input_file='leads_raw.json', output_file='leads_validated.json'):
    """
    Validate leads from input file and save to output file.

    Args:
        input_file (str): Input JSON file in .tmp/
        output_file (str): Output JSON file in .tmp/
    """
    try:
        # Load raw leads
        leads = load_json(input_file)
        print(f"Loaded {len(leads)} leads from {input_file}")

        # Validate
        validator = LeadValidator()
        results = validator.validate_leads(leads)

        # Save valid leads
        save_json(results['valid'], output_file)

        # Save invalid leads for review
        if results['invalid']:
            save_json(results['invalid'], 'leads_invalid.json')

        # Print stats
        stats = results['stats']
        log_success(
            "Lead validation complete",
            {
                'total': stats['total'],
                'valid': stats['valid'],
                'invalid_email': stats['invalid_email'],
                'duplicates': stats['duplicate'],
                'missing_fields': stats['missing_required'],
                'success_rate': f"{(stats['valid']/stats['total']*100):.1f}%"
            }
        )

        return results

    except FileNotFoundError as e:
        log_error(f"Input file not found: {e}")
        sys.exit(1)
    except Exception as e:
        log_error(f"Validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

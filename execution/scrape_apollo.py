"""
Scrape leads from Apollo.io API.
Requires APOLLO_API_KEY in .env file.
"""

import sys
import requests
from utils import (
    get_env_variable,
    save_json,
    log_error,
    log_success
)


class ApolloScraper:
    """Handle Apollo.io API interactions for lead scraping."""

    def __init__(self):
        """Initialize Apollo scraper with API key."""
        self.api_key = get_env_variable('APOLLO_API_KEY')
        self.base_url = 'https://api.apollo.io/v1'
        self.headers = {
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache',
            'X-Api-Key': self.api_key
        }

    def search_people(self, criteria):
        """
        Search for people based on criteria.

        Args:
            criteria (dict): Search criteria including:
                - person_titles: List of job titles
                - organization_num_employees_ranges: List of company size ranges
                - person_locations: List of locations
                - q_organization_domains: List of company domains
                - page: Page number (default 1)
                - per_page: Results per page (max 100)

        Returns:
            dict: API response with people and pagination info
        """
        url = f"{self.base_url}/mixed_people/search"

        # Default pagination
        if 'page' not in criteria:
            criteria['page'] = 1
        if 'per_page' not in criteria:
            criteria['per_page'] = 100

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=criteria,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            log_success(
                f"Retrieved {len(data.get('people', []))} people",
                {'page': criteria['page'], 'total_pages': data.get('pagination', {}).get('total_pages')}
            )

            return data

        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                log_error("Rate limit exceeded", {'retry_after': response.headers.get('Retry-After')})
            else:
                log_error(f"HTTP error: {e}", {'status_code': response.status_code})
            raise

        except requests.exceptions.RequestException as e:
            log_error(f"Request failed: {e}")
            raise

    def extract_lead_data(self, person):
        """
        Extract relevant fields from Apollo person object.

        Args:
            person (dict): Person object from Apollo API

        Returns:
            dict: Cleaned lead data
        """
        return {
            'first_name': person.get('first_name', ''),
            'last_name': person.get('last_name', ''),
            'email': person.get('email', ''),
            'title': person.get('title', ''),
            'linkedin_url': person.get('linkedin_url', ''),
            'company_name': person.get('organization', {}).get('name', ''),
            'company_domain': person.get('organization', {}).get('primary_domain', ''),
            'company_industry': person.get('organization', {}).get('industry', ''),
            'company_size': person.get('organization', {}).get('estimated_num_employees', ''),
            'city': person.get('city', ''),
            'state': person.get('state', ''),
            'country': person.get('country', ''),
        }

    def scrape_leads(self, criteria, max_results=100):
        """
        Scrape leads based on search criteria.

        Args:
            criteria (dict): Search criteria for Apollo API
            max_results (int): Maximum number of results to retrieve

        Returns:
            list: List of lead dictionaries
        """
        all_leads = []
        page = 1
        per_page = min(100, max_results)  # Apollo max is 100 per page

        while len(all_leads) < max_results:
            criteria['page'] = page
            criteria['per_page'] = per_page

            response = self.search_people(criteria)
            people = response.get('people', [])

            if not people:
                break

            # Extract and add leads
            for person in people:
                lead = self.extract_lead_data(person)
                all_leads.append(lead)

                if len(all_leads) >= max_results:
                    break

            # Check if there are more pages
            pagination = response.get('pagination', {})
            if page >= pagination.get('total_pages', 1):
                break

            page += 1

        # Save to .tmp
        save_json(all_leads, 'leads_raw.json')

        log_success(f"Scraped {len(all_leads)} leads", {'criteria': criteria})
        return all_leads


def main():
    """
    Example usage of Apollo scraper.
    Modify search criteria as needed.
    """
    # Example search criteria
    criteria = {
        'person_titles': ['CEO', 'Founder', 'Co-Founder'],
        'organization_num_employees_ranges': ['1,10', '11,50'],
        'person_locations': ['United States'],
    }

    scraper = ApolloScraper()
    leads = scraper.scrape_leads(criteria, max_results=100)

    print(f"\nScraped {len(leads)} leads")
    print(f"Sample lead: {leads[0] if leads else 'No leads found'}")


if __name__ == "__main__":
    main()

# Google Maps Lead Scraper with Contact Enrichment

## System Overview
Scrape local businesses from Google Maps based on search criteria, then enrich each lead with contact information by crawling their websites and extracting emails, phone numbers, and owner details using AI.

## High-Level Build Instructions

### 1. Set up Google Maps scraping tool
- Find or configure a scraping tool that can extract business listings from Google Maps (e.g., Apify Google Maps scraper)
- Set up API authentication and credentials
- Test scraper to ensure it returns: business name, category, address, phone, website URL, location coordinates
- Store API credentials in environment variables

### 2. Implement search query system
- Allow flexible search inputs: industry/business type + location (e.g., "HVAC companies in Texas")
- Support specific city/region targeting (e.g., "Dallas", "Fort Worth", "Arlington")
- Set quantity limits (e.g., scrape 100 companies)
- Enable batch processing for multiple searches

### 3. Build website crawling engine
- Extract website URLs from Google Maps results
- Crawl multiple pages per website (not just homepage)
- Target high-probability pages: /about, /team, /contact, /leadership, /founders, /owners
- Handle different website structures and URL patterns
- Set reasonable timeouts and retry logic for failed requests

### 4. Create intelligent page selection logic
- Identify which pages are most likely to contain contact information
- Look for common URL patterns: "/about-us", "/meet-the-team", "/contact", "/our-story"
- Parse site navigation menus to find relevant pages
- Prioritize pages based on likelihood of containing owner/executive contact info

### 5. Build content extraction system
- Scrape text content from all identified pages
- Compile content into a single text block per business
- Clean HTML and extract readable text
- Handle JavaScript-rendered content if necessary
- Limit text extraction to reasonable size to avoid token limits

### 6. Implement AI-powered contact extraction
- Use Claude (or similar AI) to extract structured data from scraped website text
- Define extraction schema: email addresses, phone numbers, owner name, team contacts
- Use a streamlined/efficient AI model to minimize costs
- Return data in structured JSON format for easy processing

### 7. Build email validation and filtering
- Validate extracted email addresses (proper format, domain exists)
- Filter out generic emails (info@, contact@, support@) when owner email is needed
- Prioritize personal emails over generic company emails
- Flag confidence level for each extracted email

### 8. Create Google Sheets export system
- Design sheet structure: Lead ID, Scrape Date, Search Query, Business Name, Category, Address, Phone, Email, Website, Owner Name, Team Contacts, Enrichment Status
- Add location coordinates for mapping functionality
- Include clickable links to Google Maps locations
- Color-code or flag leads based on enrichment success (email found vs. not found)

### 9. Implement incremental/batch processing
- Process leads in batches (e.g., 10-20 at a time) to minimize API costs
- Update Google Sheet incrementally as results come in
- Show progress indicators (e.g., "Processed 25/100 leads")
- Handle rate limits gracefully with delays between batches

### 10. Build contact enrichment fallback system (optional)
- Integrate with email finder tools (Hunter.io, Anymailfinder, Voila Norbert)
- Use enrichment services only when website crawl fails to find email
- Track enrichment costs per lead
- Mark enrichment source in spreadsheet (website vs. paid service)

### 11. Add data quality and deduplication
- Remove duplicate businesses (same name + same address)
- Validate phone numbers are properly formatted
- Check that addresses are complete
- Flag incomplete records for manual review
- Calculate success rate (% of leads with email addresses)

### 12. Create geographical targeting features
- Include location coordinates in output for mapping
- Allow filtering by specific cities, zip codes, or radius from a point
- Support density-based scraping (e.g., concentrate on specific neighborhoods)
- Visualize lead distribution on maps for local outreach teams

### 13. Build end-to-end workflow automation
- Chain together: Google Maps scrape → extract websites → crawl pages → AI extraction → validate contacts → export to Sheets
- Provide progress updates throughout the process
- Display final statistics: total leads scraped, emails found (%), phone numbers found (%), owner names found (%)
- Output Google Sheet link with all enriched leads

## Success Criteria
- Successfully scrape 100 businesses from Google Maps based on search criteria
- Achieve 40-50% email discovery rate through website crawling
- Extract owner/decision-maker names for majority of leads
- Export clean, structured data to Google Sheets with location mapping
- Keep cost under $0.01-0.02 per lead
- Complete full scrape + enrichment in under 15-20 minutes

## Tools & APIs Needed
- Google Maps scraper (Apify or similar)
- Web scraping library (BeautifulSoup, Puppeteer, Playwright)
- Claude API for contact extraction
- Google Sheets API
- Optional: Email enrichment services (Hunter.io, Anymailfinder, Voila Norbert)
- Optional: Email validation service

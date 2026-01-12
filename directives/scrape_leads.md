# Scrape Leads

## Goal
Scrape lead information from specified sources and compile into a structured format for outreach campaigns.

## Inputs
- Target criteria (industry, company size, location, job titles)
- Source platform (Apollo, LinkedIn, etc.)
- Number of leads desired

## Execution Tools
- `execution/scrape_apollo.py` - Scrapes leads from Apollo API
- `execution/validate_leads.py` - Validates and enriches lead data
- `execution/export_to_sheets.py` - Exports leads to Google Sheets

## Process Flow
1. Receive target criteria from user
2. Query Apollo API with search parameters
3. Extract lead data (name, email, company, title, LinkedIn)
4. Validate email addresses and remove duplicates
5. Enrich data with additional fields if needed
6. Export to Google Sheets deliverable
7. Store intermediate data in `.tmp/leads_raw.json`

## Outputs
- **Primary**: Google Sheet with validated leads (shared URL)
- **Intermediate**: `.tmp/leads_raw.json` (raw API response)
- **Intermediate**: `.tmp/leads_validated.csv` (post-validation)

## Edge Cases & Error Handling
- **API Rate Limits**: Apollo has 100 requests/minute - implement backoff
- **Invalid Emails**: Flag for manual review, don't discard
- **Duplicate Leads**: Check against existing campaigns before adding
- **Missing Data**: Note which fields are missing, don't fail the entire record

## Success Criteria
- At least 90% of leads have valid email addresses
- No duplicate emails in output
- All required fields populated (name, email, company)
- Results delivered to Google Sheet within expected timeframe

## Notes & Learnings
(Updates as the system learns)

# Send Cold Emails

## Goal
Create and send personalized cold email campaigns to scraped leads using Instantly.ai or similar email service.

## Inputs
- Google Sheet URL with lead data
- Email template with personalization variables
- Campaign settings (send schedule, daily limits, follow-up sequence)
- Subject line variations

## Execution Tools
- `execution/prepare_campaign.py` - Formats lead data for email platform
- `execution/send_via_instantly.py` - Uploads leads and sends via Instantly API
- `execution/track_campaign.py` - Monitors delivery and engagement metrics

## Process Flow
1. Load leads from Google Sheet
2. Validate required fields (email, first name, company)
3. Apply personalization to email template
4. Create campaign in Instantly
5. Upload leads to campaign
6. Set sending schedule and limits
7. Monitor initial delivery for issues
8. Update Google Sheet with campaign status

## Outputs
- **Primary**: Active campaign in Instantly with tracking URL
- **Primary**: Updated Google Sheet with campaign IDs and status
- **Intermediate**: `.tmp/campaign_payload.json` (formatted for API)

## Edge Cases & Error Handling
- **Invalid Emails**: Skip and flag in sheet, don't fail entire batch
- **Daily Send Limits**: Respect Instantly limits (200-500/day depending on plan)
- **Bounce Rates**: Monitor first 50 sends, pause if >5% bounce rate
- **API Errors**: Retry with exponential backoff, log failures
- **Template Variables Missing**: Use fallback values or skip personalization

## Success Criteria
- All valid leads uploaded to campaign
- Campaign activated successfully
- No more than 2% bounce rate on first batch
- Personalization variables properly replaced
- Tracking and reporting set up

## Notes & Learnings
(Updates as the system learns)

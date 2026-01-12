# Instantly Campaign Writer

## System Overview
Automatically generate multiple cold email campaign variations for Instantly.ai platform using high-performing templates and AI personalization. Creates split-test ready campaigns with different offer angles.

## High-Level Build Instructions

### 1. Set up Instantly.ai API integration
- Obtain Instantly API credentials and authenticate
- Test API endpoints for creating campaigns, adding sequences, and managing drafts
- Store API keys securely in environment variables
- Understand Instantly's campaign structure (sequences, steps, variants)

### 2. Build high-performing copy repository
- Collect proven cold email templates that have generated results
- Organize templates by industry, offer type, and approach (aggressive vs. consultative)
- Store templates in a searchable database or file structure
- Include metadata: subject lines, open rates, reply rates, conversion rates

### 3. Create campaign input parameter system
- Define required inputs: company name, offer details, target audience, guarantee/hook
- Allow flexible offer structures (e.g., "10 patients in 30 days or $1000", "3 free patients then performance-based")
- Accept industry-specific context (e.g., dental clinics, SaaS companies, HVAC businesses)
- Support multiple campaign variations in a single run

### 4. Implement split-testing framework
- Generate 3-5 campaign variations with different angles for the same offer
- Create variations of: subject lines, opening hooks, offer presentation, CTAs
- Ensure each variation is distinct enough to produce meaningful test results
- Label campaigns clearly (e.g., "Dental - Free Patients", "Dental - Guarantee", "Dental - Risk Reversal")

### 5. Build AI personalization engine
- Use AI to generate dynamic icebreakers based on prospect research
- Create company-specific opening lines using {{company_name}} variable
- Personalize value propositions based on industry pain points
- Ensure personalization doesn't sound generic or templated

### 6. Design email sequence structure
- Create multi-step sequences (initial email + 2-4 follow-ups)
- Space follow-ups appropriately (3-7 days apart)
- Vary the angle in follow-ups (social proof, case study, question, breakup email)
- Keep emails concise and focused on one CTA

### 7. Implement offer variation generator
- Create multiple ways to present the same core offer
- Examples: free trial, guarantee, risk reversal, social proof, scarcity
- Generate compelling subject lines for each offer variation
- Test aggressive vs. consultative tones

### 8. Build campaign creation workflow via API
- Make HTTP POST requests to Instantly API to create draft campaigns
- Upload sequences with proper formatting and personalization variables
- Set appropriate delays between sequence steps
- Verify campaigns are created successfully (check status codes)

### 9. Create campaign review and editing interface
- Provide links to review each campaign in Instantly dashboard
- Display campaign copy in readable format for quick review
- Allow easy editing of generated copy before launching
- Show all variations side-by-side for comparison

### 10. Implement best practices and compliance
- Ensure emails comply with CAN-SPAM and GDPR requirements
- Include unsubscribe mechanisms in templates
- Avoid spam trigger words and phrases
- Keep emails under 150 words for better deliverability

### 11. Add learning and optimization system
- Track which campaign variations perform best (open rate, reply rate, conversion)
- Store winning campaigns for future reference and reuse
- Identify patterns in successful copy (structure, length, offer type)
- Continuously update template repository with proven winners

### 12. Build end-to-end automation workflow
- Chain together: input offer → select templates → generate variations → create campaigns → output review links
- Provide summary of campaigns created and their key differences
- Send links to review all campaigns in Instantly dashboard
- Enable quick launch of campaigns after review

## Success Criteria
- Generate 3-5 distinct campaign variations per offer
- Create campaigns in Instantly draft status via API
- Include AI-personalized icebreakers and company-specific hooks
- Provide varied offer angles to maximize split-test effectiveness
- Reduce campaign creation time from 2-3 hours to under 15 minutes

## Tools & APIs Needed
- Instantly.ai API
- AI model for copy generation and personalization (Claude, GPT, etc.)
- Template repository (can be markdown files, database, or structured JSON)
- Campaign performance tracking (optional: integrate with Instantly analytics)

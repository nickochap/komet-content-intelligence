# Komet Content Intelligence System

## Project context
CrewAI-based content intelligence system for Komet (gokomet.com).
Australian Salesforce consultancy, education providers focus, AU/NZ market.

## Owner
Nick — CEO. Not a Python developer. Claude Code writes all Python.
Nick reviews outputs and approves content. Caden reviews Agentforce
and technical architecture claims.

## Architecture
Three CrewAI crews via CrewAI Flows:
1. Intelligence Crew — weekly autonomous, outputs ranked idea list to Slack
2. Content Crew — per approved idea, 4-agent multi-pass with revision loop
3. Creative Crew — parallel, generates images (Nano Banana) + carousels (Contentdrips)

n8n handles: scheduling triggers, Slack approval gates, LinkedIn + WordPress
publishing, Google Sheets logging. CrewAI handles: all generation and intelligence.

## Config files already on disk
config/brands/komet.yaml — brand rules (create this in Phase 2)
config/templates/content_templates.md — Writer agent reference, all post structures + worked examples
config/calendar/Komet content pipeline sheet.csv — Month 1 planned topics, seed data for intelligence crew first run

## Existing n8n credentials to mirror in .env
- Google Sheets: Sheet ID 1S43xzHTXPWlwNGUV_R_qmZ-mPRPMS85NF5zMnxVTzF4
- Slack content channel: C0AHAK5CMFB
- Slack Caden review channel: C0AGGM4225D
- GSC: sc-domain:gokomet.com
- WordPress: gokomet.com/wp-json/wp/v2/posts

## Agentforce content
Agentforce is a valid content type for Komet. The Brand Guardian checks all
Agentforce claims against official Salesforce documentation and fails content
that overclaims. Nick reviews all content including Agentforce in a single
approval gate. Nick liaises with Caden on technical accuracy separately if needed.

## Key constraints
- YAML-first: agent and task config in YAML, not hardcoded Python
- Brand config injected at runtime from config/brands/komet.yaml
- Secrets via .env only — never hardcode credentials
- UV for all package management — never pip directly
- Fail loudly: errors go to Slack C0AHAK5CMFB, never silent
- AU English: "enrolment" not "enrollment", "programme" in formal contexts

## Build approach
- Sign up for CrewAI AMP free tier at app.crewai.com before building
- Start from crewAI-examples/crews/marketing_strategy as content crew base
- Deploy to AMP using `crewai deploy push` — not local server
- AMP handles scheduling (cron), Slack triggers, and HITL approval gates
- AMP Webhook Streaming sends approved content to n8n for publishing
- Install mcp-crew-ai for running crews locally during development only
- Serper for web search (not Google Search API — simpler)

## Success test
Input: "Why most Salesforce implementations fail in education"
Expected: LinkedIn post Nick would publish with minimal edits + image URL

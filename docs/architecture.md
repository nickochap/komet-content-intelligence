# Komet Content Intelligence — System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        NICK'S WEEKLY WORKFLOW                       │
│                                                                     │
│  Monday morning:                                                    │
│    → Slack notification: "8 content ideas ranked"                   │
│    → React ✅ on the ideas you want produced                        │
│                                                                     │
│  Within ~10 minutes per idea:                                       │
│    → Slack notification: "Content package ready for review"         │
│    → Read the summary, check AMP Executions for full package        │
│    → React ✅ to approve, ❌ to reject (reply with revision notes)   │
│                                                                     │
│  After approval:                                                    │
│    → Images generated automatically                                 │
│    → WordPress draft created automatically                          │
│    → LinkedIn post text appears in Slack                            │
│    → Review WordPress draft → click Publish                         │
│    → Copy LinkedIn text from Slack → paste into LinkedIn            │
│                                                                     │
│  Total Nick effort per content piece: ~5 minutes                    │
└─────────────────────────────────────────────────────────────────────┘
```

## Complete Pipeline Flow

```
                    ┌──────────────┐
                    │   n8n CRON   │
                    │ Mon 9AM AEST │
                    └──────┬───────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   AMP: INTELLIGENCE    │
              │   CREW (4 agents)      │
              │                        │
              │  Competitor Monitor ──┐ │
              │  Trend Researcher ───┤ │
              │  Performance Analyst ┤ │
              │  Idea Generator ─────┘ │
              │                        │
              │  Output: 8-10 ranked   │
              │  content ideas         │
              └────────────┬───────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   n8n: POST TO SLACK   │
              │                        │
              │  Each idea posted as   │
              │  its own message       │
              │  "React ✅ to produce" │
              └────────────┬───────────┘
                           │
                    Nick reacts ✅
                    on an idea
                           │
                           ▼
              ┌────────────────────────┐
              │   n8n: TRIGGER AMP     │
              │                        │
              │  Extracts idea text    │
              │  POST /kickoff         │
              │  { action:             │
              │    "full_pipeline",    │
              │    content_brief:      │
              │    "<idea text>" }     │
              └────────────┬───────────┘
                           │
    ═══════════════════════╪═══════════════════════════
    ║  AMP: SINGLE EXECUTION (all content stays here) ║
    ═══════════════════════╪═══════════════════════════
                           │
                           ▼
    ┌──────────────────────────────────────────────────┐
    │              STAGE 1: CONTENT CREW               │
    │              (4 agents, sequential)               │
    │                                                   │
    │  ┌─────────────────┐                              │
    │  │ 1. STRATEGIST   │  Reads proof library         │
    │  │                 │  Produces strategy brief:     │
    │  │                 │  angle, hooks, proof IDs,     │
    │  │                 │  offer mapping, image dir     │
    │  └────────┬────────┘                              │
    │           ▼                                       │
    │  ┌─────────────────┐                              │
    │  │ 2. WRITER       │  Produces complete package:  │
    │  │                 │  LinkedIn: 10 sections        │
    │  │                 │  Blog: 9 sections (1500+w)    │
    │  │                 │  AU English, proof-backed     │
    │  └────────┬────────┘                              │
    │           ▼                                       │
    │  ┌─────────────────┐                              │
    │  │ 3. CRITIC       │  QA scores (6 dimensions)    │
    │  │                 │  Completeness check           │
    │  │                 │  Max 2 revision loops         │
    │  │                 │  Hard floors: C≥4, E≥4       │
    │  └────────┬────────┘                              │
    │           ▼                                       │
    │  ┌─────────────────┐                              │
    │  │ 4. BRAND        │  8 hard rules check:         │
    │  │    GUARDIAN      │  AU English, banned phrases, │
    │  │                 │  CTA mapping, proof refs,     │
    │  │                 │  voice, follow-ups, image     │
    │  │                 │  brief, Agentforce claims     │
    │  └────────┬────────┘                              │
    │           │                                       │
    │    ┌──────┴──────────────────────────────────┐    │
    │    │        GUARDRAIL (Python function)       │    │
    │    │                                          │    │
    │    │  1. Posts summary to Slack:               │    │
    │    │     "📋 Content ready for review"        │    │
    │    │     [first 1900 chars of package]         │    │
    │    │     "React ✅ to approve, ❌ to reject"   │    │
    │    │                                          │    │
    │    │  2. Polls Slack every 30 seconds:         │    │
    │    │                                          │    │
    │    │     ✅ reaction detected?                 │    │
    │    │     → return (True, {})                   │    │
    │    │     → crew CONTINUES to Stage 2           │    │
    │    │                                          │    │
    │    │     ❌ reaction detected?                 │    │
    │    │     → reads thread for Nick's notes       │    │
    │    │     → return (False, "Nick's feedback")   │    │
    │    │     → Brand Guardian RE-EXECUTES          │    │
    │    │       with feedback (max 2 retries)       │    │
    │    │                                          │    │
    │    │     4 hours, no reaction?                 │    │
    │    │     → timeout, pipeline stops             │    │
    │    └─────────────────────────────────────────┘    │
    │           │                                       │
    │      (approved — content_result.raw               │
    │       stays in Python memory)                     │
    │           │                                       │
    │           ▼                                       │
    │  ┌──────────────────────────────────────────┐     │
    │  │         STAGE 2: CREATIVE CREW            │     │
    │  │         (1 agent)                         │     │
    │  │                                           │     │
    │  │  Input: content_result.raw                │     │
    │  │  (exact bytes — no serialization)         │     │
    │  │                                           │     │
    │  │  → Reads image brief from content pack    │     │
    │  │  → Generates hero image (Nano Banana)     │     │
    │  │  → Generates carousel PDF (Contentdrips)  │     │
    │  │  → Returns IMAGE_URL + CAROUSEL_PDF_URL   │     │
    │  └──────────────────┬───────────────────────┘     │
    │                     │                             │
    │                (same process)                      │
    │                     │                             │
    │                     ▼                             │
    │  ┌──────────────────────────────────────────┐     │
    │  │         STAGE 3: PUBLISHER CREW           │     │
    │  │         (1 agent)                         │     │
    │  │                                           │     │
    │  │  Input: content_result.raw                │     │
    │  │       + creative_result.raw               │     │
    │  │  (both from Python memory)                │     │
    │  │                                           │     │
    │  │  WORDPRESS:                               │     │
    │  │  → Creates DRAFT on gokomet.com           │     │
    │  │  → Title: SEO TITLE from package          │     │
    │  │  → Body: full article (never truncated)   │     │
    │  │  → Status: DRAFT (never live)             │     │
    │  │  → Returns: draft URL                     │     │
    │  │                                           │     │
    │  │  LINKEDIN:                                │     │
    │  │  → Posts full text + image to SLACK       │     │
    │  │  → Nick copy-pastes to LinkedIn manually  │     │
    │  │  → (Avoids token expiry, accidental post) │     │
    │  └──────────────────┬───────────────────────┘     │
    │                     │                             │
    └─────────────────────┼─────────────────────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │   SLACK NOTIFICATION   │
              │                        │
              │  🚀 Content published  │
              │                        │
              │  WordPress draft:      │
              │  [gokomet.com/draft]   │
              │                        │
              │  LinkedIn text ready   │
              │  to copy-paste above   │
              │                        │
              │  Review WordPress →    │
              │  click Publish when    │
              │  ready                 │
              └────────────────────────┘
```

## Data Flow — What Goes Where

```
CONTENT NEVER LEAVES AMP:

  Strategist output ──→ Writer input    (Python memory)
  Writer output     ──→ Critic input    (Python memory)
  Critic output     ──→ Guardian input  (Python memory)
  Guardian output   ──→ GUARDRAIL       (Python memory)
  Guardian output   ──→ Creative input  (Python memory, via dispatcher)
  Guardian output   ──→ Publisher input (Python memory, via dispatcher)
  Creative output   ──→ Publisher input (Python memory, via dispatcher)

ONLY SUMMARIES GO TO SLACK:

  Guardrail → Slack: first 1900 chars of content package
  Publisher → Slack: WordPress draft URL + LinkedIn post text
  Intelligence → Slack (via n8n): idea summaries

N8N NEVER TOUCHES CONTENT:

  n8n → AMP: { action: "full_pipeline", content_brief: "topic..." }
  n8n → Slack: intelligence idea messages
  n8n → AMP: trigger kickoff (HTTP POST, no content in body)
```

## The Guardrail — How Approval Actually Works

```
NICK'S EXPERIENCE IN SLACK:

  ┌──────────────────────────────────────────────────────┐
  │ Komet n8N APP  10:15 AM                              │
  │                                                      │
  │ 📋 Content Package — Awaiting Approval               │
  │                                                      │
  │ BRAND GUARDIAN REVIEW — KOMET-STRAT-001              │
  │ STATUS: APPROVED                                     │
  │                                                      │
  │ ## FINAL POST                                        │
  │ Your Salesforce went live six months ago. Your        │
  │ admissions team is still working from spreadsheets... │
  │ [preview continues ~1900 chars]                      │
  │                                                      │
  │ React ✅ to approve and continue to image generation. │
  │ React ❌ to reject (reply in thread with notes).      │
  │                                                      │
  │  ✅ 1    ❌                                           │
  │                                                      │
  │  └── Nick reacted with ✅                             │
  │                                                      │
  │  ┌─ Thread ──────────────────────────────────────┐   │
  │  │ Komet n8N: ✅ Approved. Proceeding to          │   │
  │  │ image generation.                              │   │
  │  └────────────────────────────────────────────────┘   │
  └──────────────────────────────────────────────────────┘

  IF NICK REJECTS:

  ┌──────────────────────────────────────────────────────┐
  │  ❌ 1                                                │
  │                                                      │
  │  └── Nick reacted with ❌                             │
  │                                                      │
  │  ┌─ Thread ──────────────────────────────────────┐   │
  │  │ Nick: Make the hook sharper — the first line   │   │
  │  │ needs to name the specific pain, not a generic │   │
  │  │ statement about Salesforce.                    │   │
  │  │                                                │   │
  │  │ Komet n8N: ❌ Rejected. Revision loop          │   │
  │  │ triggered with feedback.                       │   │
  │  └────────────────────────────────────────────────┘   │
  │                                                      │
  │  [Brand Guardian re-executes with Nick's feedback]   │
  │  [New package posted for review — max 2 retries]     │
  └──────────────────────────────────────────────────────┘
```

## Weekly Rhythm

```
MONDAY 9AM AEST
  Intelligence Crew runs autonomously (triggered by n8n cron)
  │
  └─→ Slack: 8-10 ideas posted as individual messages

MONDAY-TUESDAY (Nick's review window)
  Nick reacts ✅ on 3-4 ideas he wants produced
  │
  └─→ Each reaction triggers a full pipeline execution on AMP

THROUGHOUT THE WEEK (automated, ~10 min per piece)
  For each approved idea:
  │
  ├── Content Crew runs (~5 min)
  ├── Guardrail posts to Slack for approval
  │     Nick reacts ✅ (or ❌ with notes for revision)
  ├── Creative Crew generates images (~2 min)
  ├── Publisher creates WordPress draft + LinkedIn text
  └── Nick gets Slack notification with URLs

NICK'S PUBLISHING (manual, ~2 min per piece)
  ├── Open WordPress draft → quick visual check → Publish
  └── Copy LinkedIn text from Slack → paste into LinkedIn
      (timing: Nick chooses when to post)
```

## Execution Budget (AMP Free Tier: 50/month)

```
Weekly:
  1x Intelligence Crew                    =  1 execution
  3-4x Content Pipeline (full_pipeline)   =  3-4 executions
                                          ─────────────
  Total per week                          =  4-5 executions

Monthly:
  4x Intelligence                         =  4 executions
  12-16x Content Pipelines                = 12-16 executions
                                          ─────────────
  Total per month                         = 16-20 executions
  Free tier limit                         = 50 executions
  Headroom                                = 30-34 executions (60-68%)
```

## What Gets Deployed

```
AMP (single deployment):
  src/komet_content_intelligence/
  ├── main.py              ← entry point, calls dispatcher
  ├── dispatcher.py        ← chains Content → Creative → Publisher
  ├── guardrails.py        ← Slack polling approval gate
  ├── crew.py              ← agent/task definitions (content crew)
  ├── config/
  │   ├── agents.yaml      ← 5 agent configs
  │   └── tasks.yaml       ← 5 task configs
  └── tools/
      ├── proof_library.py
      ├── wordpress_publisher.py
      └── linkedin_publisher.py

n8n (2 workflows):
  1. Weekly Intelligence Trigger
     Schedule → AMP kickoff → poll → post ideas to Slack
  2. Content Pipeline Trigger
     Slack reaction → extract idea → AMP kickoff
```

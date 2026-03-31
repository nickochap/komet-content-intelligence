# Komet Content Templates — Writer Agent Reference

**Version:** v1 | February 2026  
**Purpose:** Structural templates and worked examples for the Writer agent.  
**Usage:** Inject as context into the Writer agent's task. Follow structures exactly.  
**Placement in project:** `config/templates/content_templates.md`

---

## LinkedIn Post — General Rules

- Length: 800–1,300 characters
- First line = hook (visible before "see more") — must create tension or curiosity without it
- Max 3 hashtags — always last line
- Zero emojis
- CTA is always the last line before hashtags
- Short paragraphs: 1–3 lines maximum
- AU English throughout

---

## LinkedIn Template 1 — Teardown ("where things break")

Use when: exposing a failure mode the ICP recognises. High resonance with admissions leaders and ops teams.

| Element | Structure |
|---------|-----------|
| **Hook (line 1)** | Cost-of-inaction or numbered failure list. Must create tension. |
| **Problem (2–3 lines)** | Describe the failure mode in specific, recognisable terms. Use education or industry context. |
| **Causes (3–5 short items)** | List the root causes. Each one is one line. Specific, not vague. Bullet points acceptable here. |
| **Fix pattern (2–3 lines)** | Simple, actionable. What to check or change. Not a full how-to — just enough to show you know the answer. |
| **CTA (last line)** | Specific to the offer. Maps to Offer A, B, or C. |
| **Hashtags** | #Salesforce #EducationCRM #[topic] |

### Worked example (Teardown):

```
5 places education leads disappear between your website and admissions.

If your admissions team is telling you "we don't get enough leads" but your 
website traffic looks fine, the leads aren't missing. They're leaking.

Here's where we typically find them:

• Form submissions that don't reach Salesforce (integration failure, no error alerting)
• Leads created but unassigned (no routing rules, or rules that don't match intake/program)
• Assigned but not contacted within 24 hours (no SLA, no escalation)
• Agent referrals duplicated or mis-routed (no dedupe on create, no source-based handling)
• Leads marked "contacted" with no next action scheduled (ownership without follow-through)

The fix isn't a new tool. It's routing rules, SLA timers, integration monitoring, 
and stage definitions that match how your admissions team actually works.

We map this in 30 minutes. Book an admissions pipeline reality check: [link]

#Salesforce #EducationCRM #Admissions
```

---

## LinkedIn Template 2 — Pattern ("how we solve it")

Use when: demonstrating a specific repeatable fix. Works well for technical/ops audiences.

| Element | Structure |
|---------|-----------|
| **Hook (line 1)** | Pattern reveal or counterintuitive statement. Creates curiosity. |
| **Context (2–3 lines)** | When this pattern applies. What problem it solves. Make it recognisable. |
| **The pattern (3–5 lines)** | Clear, numbered or structured steps. What gets configured, what fires, what the user sees. |
| **Trade-off or caveat (1–2 lines)** | What this doesn't solve, or the prerequisite. Shows honesty. |
| **CTA (last line)** | Links to relevant offer. |

---

## LinkedIn Template 3 — Opinionated Take ("our view")

Use when: staking out a position on an industry assumption. Best for engagement and shares.

| Element | Structure |
|---------|-----------|
| **Hook (line 1)** | Myth-bust or counterintuitive. Bold but defensible. |
| **The opinion (2–3 lines)** | State the position clearly. Frame as "in our experience" or "our view." |
| **Evidence / reasoning (3–4 lines)** | Why we hold this view. Reference patterns, client work (anonymised), or observable industry behaviour. |
| **Concession (1 line)** | Acknowledge the other side or nuance. Prevents tribal tone. |
| **CTA (last line)** | Relevant offer or open question to drive engagement. |

---

## LinkedIn Template 4 — Case Study Snippet

Use when: sharing a client outcome. Always result-first. All metrics must reference proof library.

| Element | Structure |
|---------|-----------|
| **Hook (line 1)** | Result-first. Lead with the outcome, not the setup. |
| **Context (1–2 lines)** | Anonymised client type + the problem they had. Brief. |
| **What we did (2–3 lines)** | Pattern/approach. Specific enough to be credible. |
| **Result (1–2 lines)** | Metric or specific qualitative outcome. Must be provable via proof library ref. |
| **Lesson (1 line)** | The generalised takeaway others can apply. |
| **CTA** | Offer A typically. |

---

## LinkedIn Output Pack — Required Fields

Every LinkedIn content pack must include all of the following:

```
FINAL POST
[publishable post — 800–1,300 characters]

ALTERNATE HOOK 1
[alternative first line — different angle]

ALTERNATE HOOK 2
[alternative first line — different style]

ALTERNATE CTA
[alternative final line — different offer or framing]

FOLLOW-UP COMMENT 1
[post in first hour — adds a detail, example, or clarifying point]

FOLLOW-UP COMMENT 2
[post in first hour — poses a question to drive engagement]

FOLLOW-UP COMMENT 3
[post in first hour — links to related resource or expands on the fix]

IMAGE BRIEF
[describe exactly what the image should show — visual type, text overlay if any,
 tone: professional/authoritative not aspirational]

RATIONALE
[2–3 sentences: why this angle works for this ICP at this stage of funnel]

QA METADATA
- Word count: [n]
- Content type: [teardown / pattern / opinionated take / case study]
- Product anchor: [Sales Cloud / Education Cloud / MC / Agentforce / Integrations]
- Offer mapping: [A / B / C]
- CTA variant: [exact text from offer map]
- Proof refs used: [MS-XX, P-XX]
- AGENTFORCE_CONTENT: [true / false]
```

---

## Blog Post — General Rules

- Length: 800–1,500 words (minimum 700 words per brief requirement)
- Structure: Problem → Pattern → Application → Checklist/CTA
- One product anchor per post
- SEO: target keyword in H1 title, first 100 words, and at least one H2
- FAQ schema via Yoast: 3–5 questions with direct answers (2–3 sentences each)
- Internal link to pillar page for the relevant cluster
- Meta description: under 160 characters, include target keyword

---

## Blog Template 1 — Problem → Pattern (the workhorse)

The standard format. Use for most education and cross-industry posts.

| Section | Length | What goes here |
|---------|--------|----------------|
| **Title (H1)** | < 70 chars | Target keyword + clear value. No clickbait. |
| **Meta description** | < 160 chars | Problem + hint at solution + target keyword. |
| **Intro / Direct answer** | 100–150 words | Answer the target question directly (AEO). State the problem. Why it matters. What this post covers. |
| **The problem (H2)** | 200–300 words | Describe the failure mode in detail. Education-specific context: intakes, programs, agents, admissions. Make it recognisable. |
| **The pattern (H2)** | 300–400 words | Solution approach. Step-by-step or structured. Name the Salesforce product and what gets configured. Include trade-offs. |
| **Application / example (H2)** | 150–250 words | How this looks in practice. Anonymised client example (proof library ref) or hypothetical walkthrough. |
| **Checklist / takeaways (H2)** | 100–150 words | 5–7 item checklist. Audit-style: "Check if [X]. If not, [Y]." |
| **CTA section** | 50–100 words | Specific offer + booking link. Reinforce urgency. Not salesy — helpful. |
| **FAQ (Yoast schema)** | 3–5 questions | Direct questions from content calendar. 2–3 sentence answers. These power AEO. |

---

## Blog Template 2 — Product Truth ("what [X] actually does")

Use for product evaluation posts. Agentforce blog in Month 1 uses this template.  
Requires Caden technical review if product is Agentforce.

| Section | Length | What goes here |
|---------|--------|----------------|
| **Title (H1)** | < 70 chars | "[Product] for [audience]: What It Does, What It Doesn't, and Where to Start" |
| **Intro / Direct answer** | 100–150 words | Honest one-paragraph summary. What this product is and isn't. Set expectations upfront. |
| **What it does well (H2)** | 250–350 words | Specific capabilities with education examples. Reference Salesforce documentation. |
| **What it doesn't solve (H2)** | 200–300 words | Gaps, prerequisites, things you still need to design. The honesty section — builds trust. |
| **Where to start (H2)** | 150–200 words | Recommended first steps. Diagnostic approach. What to evaluate before committing. |
| **CTA + FAQ** | Standard | As per Template 1. |

---

## Blog Output Pack — Required Fields

```
ARTICLE
[full article — minimum 700 words, structured per template]

META DESCRIPTION
[under 160 characters — target keyword included]

SEO TITLE
[under 60 characters — target keyword in first 3 words if possible]

TARGET KEYWORD
[primary keyword for this post]

DERIVED LINKEDIN POST
[150–200 word LinkedIn post based on the article — different angle to the article title]

REPURPOSED SNIPPET 1
[standalone insight from article — suitable for future LinkedIn post or comment]

REPURPOSED SNIPPET 2
[standalone insight — different section of article]

REPURPOSED SNIPPET 3
[standalone insight — practical or checklist-style]

IMAGE BRIEF
[describe hero image — professional/authoritative B2B, dark navy + teal palette]

FAQ QUESTIONS (3–5)
Q1: [question]
A1: [2–3 sentence direct answer]
[repeat]

QA METADATA
- Word count: [n]
- Content type: [product truth / teardown / pattern]
- Product anchor: [Sales Cloud / Education Cloud / MC / Agentforce / Integrations]
- Offer mapping: [A / B / C]
- CTA variant: [exact text]
- Proof refs used: [MS-XX, P-XX or "none — hypothetical example used"]
- Internal link target: [pillar page]
- Cluster: [C1–C5]
- AGENTFORCE_CONTENT: [true / false]
```

---

## Case Study Template (anonymised)

Length: 1,000–1,500 words. Published as blog post. Every claim must reference proof library.

| Section | Length | What goes here |
|---------|--------|----------------|
| **Title** | < 70 chars | Result-first: "How [type of org] [achieved outcome] with [pattern/product]" |
| **Snapshot (sidebar)** | 50 words | Client type (anonymised), segment, team size, Salesforce products, engagement type (A/B/C), timeline. |
| **The situation** | 150–250 words | What the organisation looked like before. Specific, recognisable problem. Pain points from ICP pain library. |
| **The approach** | 250–350 words | What Komet did. Patterns used, products configured, governance changes made. Specific and repeatable. |
| **The results** | 150–200 words | Metrics or qualitative outcomes. Every claim must reference proof library ID. No vague "improved efficiency." |
| **Lessons** | 100–150 words | Generalised takeaways. What worked, what was harder than expected, what we'd recommend to a similar org. |
| **CTA** | 50–100 words | Offer A typically. "If this sounds like your situation, book a 30-minute admissions reality check." |

---

## Pre-Publish Metadata Checklist (all assets)

The Brand Guardian checks all of these before issuing APPROVED status:

| Field | Required |
|-------|----------|
| Asset title | ✓ |
| Asset type (LinkedIn / Blog / Case study) | ✓ |
| Content type (pattern / teardown / opinionated take / case study / product truth) | ✓ |
| Industry (education / cross-industry) | ✓ |
| Product anchor (Sales Cloud / Education Cloud / MC / Agentforce / Integrations) | ✓ |
| Offer mapping (A / B / C) | ✓ |
| CTA text — exact wording from offer map | ✓ |
| Proof library reference IDs | ✓ (or "none — labelled opinion") |
| Target keyword | ✓ (blog only) |
| Cluster (C1–C5) | ✓ |
| FAQ questions (3–5) | ✓ (blog only) |
| Visual required | ✓ LinkedIn: always. Blog: header + inline if applicable. |
| Hashtags | ✓ LinkedIn: max 3 |
| Internal link target | ✓ Blog: which pillar page? |
| QA scorecard completed | ✓ |
| AGENTFORCE_CONTENT flag | ✓ (Caden review required if true) |

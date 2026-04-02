"""
Dispatcher — plain Python orchestrator for the Komet content pipeline.

No CrewAI Flows, no @persist, no @human_feedback. Just crew.kickoff()
chained sequentially in the same Python process. Content stays in memory.

Actions:
  full_pipeline — Content Crew → Creative Crew → Publisher Crew
  intelligence  — Intelligence Crew (weekly autonomous)
"""

import os
import yaml
import json
from pathlib import Path
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, task, crew
from dotenv import load_dotenv

load_dotenv()

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "not-used"

from komet_content_intelligence.tools.proof_library import ProofLibraryTool
from komet_content_intelligence.tools.wordpress_publisher import WordPressPublisherTool
from komet_content_intelligence.tools.linkedin_publisher import LinkedInPublisherTool
from komet_content_intelligence.guardrails import approval_guardrail

claude_llm = LLM(
    model="anthropic/claude-sonnet-4-6",
    max_tokens=32768,
)


def load_brand_config(brand: str = "komet") -> dict:
    for base in [Path(__file__).parent.parent.parent, Path.cwd()]:
        config_path = base / f"config/brands/{brand}.yaml"
        if config_path.exists():
            break
    with open(config_path) as f:
        return yaml.safe_load(f)


def run_pipeline(inputs: dict) -> str:
    """
    Full content pipeline: Content → Creative → Publisher.
    Content stays in Python memory between crews — no serialization.
    """
    from komet_content_intelligence.slack_notifier import SlackNotifier
    notifier = SlackNotifier()

    # --- Stage 1: Content Crew (4 agents + guardrail approval gate) ---
    content_crew = _build_content_crew()
    content_result = content_crew.kickoff(inputs=inputs)

    # Check Brand Guardian approved (guardrail handles the gate)
    if "APPROVED" not in content_result.raw[:500].upper():
        notifier.send_error_alert(
            "Content pipeline stopped — Brand Guardian did not approve.",
            node="dispatcher.run_pipeline",
        )
        return json.dumps({"status": "rejected", "reason": content_result.raw[:300]})

    # --- Stage 2: Creative Crew (1 agent — uses approved content directly) ---
    creative_crew = _build_creative_crew()
    creative_result = creative_crew.kickoff(
        inputs={"content_pack": content_result.raw}
    )

    # --- Stage 3: Publisher Crew (1 agent — gets both content + creative) ---
    publisher_crew = _build_publisher_crew()
    publish_result = publisher_crew.kickoff(inputs={
        "content_pack": content_result.raw,
        "creative_asset": creative_result.raw,
        "content_type": inputs.get("content_type", "both"),
    })

    # Notify completion
    try:
        log = json.loads(publish_result.raw)
    except (json.JSONDecodeError, TypeError):
        log = {"raw": publish_result.raw[:500]}

    notifier.send_publish_complete(
        topic=inputs.get("content_brief", "")[:80],
        wp_url=log.get("wordpress_draft_url", ""),
        linkedin_url=log.get("linkedin_url", ""),
    )

    return publish_result.raw


def run_intelligence(inputs: dict) -> str:
    """Weekly intelligence crew — outputs ranked idea list."""
    intelligence_crew = _build_intelligence_crew()
    result = intelligence_crew.kickoff(inputs=inputs)
    return result.raw


# --- Crew builders ---
# These build crews from the config YAML files. Each is self-contained.


def _build_content_crew() -> Crew:
    """4-agent content crew with guardrail on brand_check_task."""
    proof_tool = ProofLibraryTool()

    strategist = Agent(
        role="Content Strategist",
        goal="Analyse brief and produce strategy document",
        backstory="Senior B2B content strategist, education + Salesforce expertise.",
        tools=[proof_tool],
        verbose=True,
        llm=claude_llm,
    )
    writer = Agent(
        role="Content Writer",
        goal="Produce complete, publish-ready content packages",
        backstory="Specialist B2B writer — Salesforce, education, AU/NZ.",
        verbose=True,
        llm=claude_llm,
    )
    critic = Agent(
        role="Content Critic and Editor",
        goal="Score quality on 6 dimensions, enforce completeness",
        backstory="Ruthless but constructive editor. Zero tolerance for generic content.",
        verbose=True,
        llm=claude_llm,
    )
    guardian = Agent(
        role="Brand Guardian",
        goal="Hard rules binary check — APPROVED or FAIL",
        backstory="Final quality gate. Knows every brand rule and AU English requirement.",
        verbose=True,
        llm=claude_llm,
    )

    # Load task configs
    config_dir = Path(__file__).parent / "config"
    with open(config_dir / "tasks.yaml") as f:
        tasks_config = yaml.safe_load(f)

    strategy_task = Task(
        description=tasks_config["strategy_task"]["description"],
        expected_output=tasks_config["strategy_task"]["expected_output"],
        agent=strategist,
    )
    writing_task = Task(
        description=tasks_config["writing_task"]["description"],
        expected_output=tasks_config["writing_task"]["expected_output"],
        agent=writer,
        context=[strategy_task],
    )
    critique_task = Task(
        description=tasks_config["critique_task"]["description"],
        expected_output=tasks_config["critique_task"]["expected_output"],
        agent=critic,
        context=[writing_task],
    )
    brand_check_task = Task(
        description=tasks_config["brand_check_task"]["description"],
        expected_output=tasks_config["brand_check_task"]["expected_output"],
        agent=guardian,
        context=[critique_task],
        output_file="outputs/content_pack.md",
        guardrail=approval_guardrail,
        guardrail_max_retries=2,
    )

    return Crew(
        agents=[strategist, writer, critic, guardian],
        tasks=[strategy_task, writing_task, critique_task, brand_check_task],
        process=Process.sequential,
        verbose=True,
        memory=True,
    )


def _build_creative_crew() -> Crew:
    """1-agent creative crew — generates images + carousels."""
    from komet_content_intelligence.tools.nano_banana import NanoBananaTool
    from komet_content_intelligence.tools.contentdrips import ContentdripsTool

    creative_director = Agent(
        role="Creative Director",
        goal="Generate visual assets matching the approved content",
        backstory="Visual designer for B2B professional services. Komet brand palette: dark navy + teal.",
        tools=[NanoBananaTool(), ContentdripsTool()],
        verbose=True,
        llm=claude_llm,
    )

    creative_task = Task(
        description=(
            "Generate visual assets for the approved content package:\n\n"
            "{content_pack}\n\n"
            "1. Read the content to identify key themes and any image brief\n"
            "2. Generate a hero image using the Image Generator tool\n"
            "   - Komet visual identity: dark navy + teal, professional B2B\n"
            "   - No lifestyle photography or aspirational student imagery\n"
            "   - Aspect ratio: 4:5 for LinkedIn, 16:9 for blog hero\n"
            "3. If carousel format specified: generate carousel PDF (max 8 slides)\n"
            "4. Return all asset URLs\n\n"
            "Output format:\n"
            "IMAGE_URL: [url]\n"
            "CAROUSEL_PDF_URL: [url if applicable]"
        ),
        expected_output="Structured asset list with URLs for all generated visuals.",
        agent=creative_director,
    )

    return Crew(
        agents=[creative_director],
        tasks=[creative_task],
        process=Process.sequential,
        verbose=True,
    )


def _build_publisher_crew() -> Crew:
    """1-agent publisher crew — WordPress draft + LinkedIn text to Slack."""
    wp_tool = WordPressPublisherTool()
    li_tool = LinkedInPublisherTool()

    publisher = Agent(
        role="Content Publisher",
        goal="Publish approved content: WordPress draft + LinkedIn text to Slack",
        backstory="Reliable publishing ops. Always create WordPress drafts, never live. LinkedIn text goes to Slack for Nick to copy-paste.",
        tools=[wp_tool, li_tool],
        verbose=True,
        llm=claude_llm,
    )

    publish_task = Task(
        description=(
            "Publish the approved content package.\n\n"
            "Content pack: {content_pack}\n"
            "Creative assets: {creative_asset}\n"
            "Content type: {content_type}\n\n"
            "For BLOG ARTICLE (package contains ARTICLE section):\n"
            "  - Use WordPress Publisher tool to create a DRAFT post\n"
            "  - Title: SEO TITLE from the package\n"
            "  - Body: full ARTICLE content — do not truncate\n"
            "  - Excerpt: META DESCRIPTION from the package\n"
            "  - Status: draft (ALWAYS draft — Nick publishes manually)\n"
            "  - Return: WordPress draft URL\n\n"
            "For LINKEDIN POST (package contains FINAL POST without ARTICLE):\n"
            "  - Do NOT use the LinkedIn Publisher tool\n"
            "  - Instead, include the full FINAL POST text in your output\n"
            "  - Nick will copy-paste to LinkedIn manually\n\n"
            "Final output must be a JSON log record:\n"
            '{{\n'
            '  "topic": "extracted from package",\n'
            '  "content_type": "linkedin_post | blog_article",\n'
            '  "linkedin_url": null,\n'
            '  "wordpress_draft_url": "URL or null",\n'
            '  "linkedin_text": "full FINAL POST text for Nick to copy-paste",\n'
            '  "published_at": "ISO timestamp",\n'
            '  "status": "draft_created | error",\n'
            '  "errors": []\n'
            "}}"
        ),
        expected_output="JSON log record confirming publish actions with URLs.",
        agent=publisher,
    )

    return Crew(
        agents=[publisher],
        tasks=[publish_task],
        process=Process.sequential,
        verbose=True,
    )


def _build_intelligence_crew() -> Crew:
    """4-agent intelligence crew — weekly autonomous research."""
    from komet_content_intelligence.tools.web_search import WebSearchTool
    from komet_content_intelligence.tools.gsc_metrics import GSCMetricsTool
    from komet_content_intelligence.tools.linkedin_metrics import LinkedInMetricsTool

    web_search = WebSearchTool()
    gsc_tool = GSCMetricsTool()
    li_metrics = LinkedInMetricsTool()

    competitor_monitor = Agent(
        role="Competitor Monitor",
        goal="Search for content from AU/NZ Salesforce partners and education tech consultants",
        backstory="Competitive intelligence analyst for B2B professional services in AU/NZ.",
        tools=[web_search],
        verbose=True,
        llm=claude_llm,
    )
    trend_researcher = Agent(
        role="Trend Researcher",
        goal="Identify 5-7 trending topics relevant to Komet's ICP",
        backstory="Content intelligence researcher for B2B education technology.",
        tools=[web_search],
        verbose=True,
        llm=claude_llm,
    )
    performance_analyst = Agent(
        role="Performance Analyst",
        goal="Analyse Komet's recent LinkedIn and GSC performance",
        backstory="Digital marketing analyst for B2B professional services.",
        tools=[gsc_tool, li_metrics],
        verbose=True,
        llm=claude_llm,
    )
    idea_generator = Agent(
        role="Content Idea Generator",
        goal="Synthesise research into 8-10 ranked content ideas",
        backstory="Senior content strategist translating market intelligence into content plans.",
        verbose=True,
        llm=claude_llm,
    )

    competitor_task = Task(
        description="Search for AU/NZ Salesforce partner content. Identify topics, engagement signals, gaps Komet could own.",
        expected_output="Structured competitive content map.",
        agent=competitor_monitor,
    )
    trend_task = Task(
        description="Search for what Komet's ICP is searching for: Salesforce in education AU/NZ, admissions, student lifecycle, AI in education, Agentforce.",
        expected_output="5-7 trending topics with search evidence.",
        agent=trend_researcher,
    )
    performance_task = Task(
        description="Analyse Komet's LinkedIn performance and GSC data. Identify top performers, underperformers, keyword opportunities.",
        expected_output="Performance summary with actionable signals.",
        agent=performance_analyst,
    )
    idea_task = Task(
        description=(
            "Synthesise competitor, trend, and performance insights into 8-10 ranked content ideas. "
            "Each idea: topic, angle, hook, format (LinkedIn/blog), proof items (MS/P IDs), "
            "offer mapping (A/B/C), rationale tied to ICP pain point, AGENTFORCE flag if applicable. "
            "60% education wedge. Rank by expected ICP impact."
        ),
        expected_output="Ranked list of 8-10 content ideas with all required fields.",
        agent=idea_generator,
        context=[competitor_task, trend_task, performance_task],
    )

    return Crew(
        agents=[competitor_monitor, trend_researcher, performance_analyst, idea_generator],
        tasks=[competitor_task, trend_task, performance_task, idea_task],
        process=Process.sequential,
        verbose=True,
        memory=True,
    )

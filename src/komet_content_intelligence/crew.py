import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Ensure OPENAI_API_KEY is available for CrewAI provider detection
# Try our custom env var names first, then fall back to not-used
for _key_name in ["DALLE_IMAGE_KEY", "DALLE_API_KEY", "OPENAI_API_KEY"]:
    _k = os.environ.get(_key_name, "")
    if _k and _k.startswith("sk-"):
        os.environ["OPENAI_API_KEY"] = _k
        break
else:
    if not os.environ.get("OPENAI_API_KEY", "").startswith("sk-"):
        os.environ["OPENAI_API_KEY"] = "not-used"

from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, task, crew
from komet_content_intelligence.tools.proof_library import ProofLibraryTool
from komet_content_intelligence.tools.wordpress_publisher import WordPressPublisherTool
from komet_content_intelligence.tools.dalle_image import DalleImageTool
from komet_content_intelligence.tools.contentdrips import ContentdripsTool
from komet_content_intelligence.tools.slack_poster import SlackPosterTool
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


@CrewBase
class KometContentIntelligenceCrew:
    """
    Komet Content Pipeline — 6 agents, sequential.
    Strategist → Writer → Critic → Brand Guardian [guardrail: Slack approval]
    → Creative Director → Publisher
    """
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self, brand: str = "komet"):
        self.brand_config = load_brand_config(brand)
        self.proof_tool = ProofLibraryTool()
        self.wp_tool = WordPressPublisherTool()
        self.image_tool = DalleImageTool()
        self.carousel_tool = ContentdripsTool()
        self.slack_poster = SlackPosterTool()

    # --- All agents (AMP auto-discovery requires all to be defined) ---

    @agent
    def content_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config["content_strategist"],
            tools=[self.proof_tool],
            verbose=True,
            llm=claude_llm,
        )

    @agent
    def content_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["content_writer"],
            verbose=True,
            llm=claude_llm,
        )

    @agent
    def content_critic(self) -> Agent:
        return Agent(
            config=self.agents_config["content_critic"],
            verbose=True,
            llm=claude_llm,
        )

    @agent
    def brand_guardian(self) -> Agent:
        return Agent(
            config=self.agents_config["brand_guardian"],
            verbose=True,
            llm=claude_llm,
        )

    @agent
    def creative_director(self) -> Agent:
        return Agent(
            config=self.agents_config["creative_director"],
            tools=[self.image_tool, self.carousel_tool],
            verbose=True,
            llm=claude_llm,
        )

    @agent
    def content_publisher(self) -> Agent:
        return Agent(
            config=self.agents_config["content_publisher"],
            tools=[self.wp_tool, self.slack_poster],
            verbose=True,
            llm=claude_llm,
        )

    @agent
    def slack_approval_monitor(self) -> Agent:
        return Agent(
            config=self.agents_config["slack_approval_monitor"],
            verbose=True,
            llm=claude_llm,
        )

    # --- All tasks (AMP auto-discovery requires all to be defined) ---

    @task
    def strategy_task(self) -> Task:
        return Task(config=self.tasks_config["strategy_task"])

    @task
    def writing_task(self) -> Task:
        return Task(config=self.tasks_config["writing_task"])

    @task
    def critique_task(self) -> Task:
        return Task(config=self.tasks_config["critique_task"])

    @task
    def brand_check_task(self) -> Task:
        return Task(
            config=self.tasks_config["brand_check_task"],
            output_file="outputs/content_pack.md",
            guardrail=approval_guardrail,
            guardrail_max_retries=2,
        )

    @task
    def creative_task(self) -> Task:
        return Task(config=self.tasks_config["creative_task"])

    @task
    def publish_task(self) -> Task:
        return Task(config=self.tasks_config["publish_task"])

    @task
    def slack_approval_task(self) -> Task:
        return Task(config=self.tasks_config["slack_approval_task"])

    # --- Crew: full pipeline ---
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[
                self.content_strategist(),
                self.content_writer(),
                self.content_critic(),
                self.brand_guardian(),
                self.creative_director(),
                self.content_publisher(),
            ],
            tasks=[
                self.strategy_task(),
                self.writing_task(),
                self.critique_task(),
                self.brand_check_task(),
                self.creative_task(),
                self.publish_task(),
            ],
            process=Process.sequential,
            verbose=True,
            memory=False,
        )

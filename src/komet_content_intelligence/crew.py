import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# CrewAI requires OPENAI_API_KEY at import time even when using Claude
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "not-used"

from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, task, crew
from komet_content_intelligence.tools.proof_library import ProofLibraryTool
from komet_content_intelligence.tools.wordpress_publisher import WordPressPublisherTool
from komet_content_intelligence.tools.linkedin_publisher import LinkedInPublisherTool

# Configure Claude with generous max_tokens for long content packages
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
    Komet Content Intelligence Crew.

    Single pipeline: Strategist → Writer → Critic → Brand Guardian → [HITL pause] → Publisher.
    Brand Guardian task has human_input=True which pauses for Nick's approval via webhook.
    After approval, Publisher continues in the same execution.

    Input: content_brief (topic, format, audience, product anchor)
    """
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self, brand: str = "komet"):
        self.brand_config = load_brand_config(brand)
        self.proof_tool = ProofLibraryTool()
        self.wp_tool = WordPressPublisherTool()
        self.li_tool = LinkedInPublisherTool()

    # --- Content agents ---

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

    # --- Publisher agent ---

    @agent
    def content_publisher(self) -> Agent:
        return Agent(
            config=self.agents_config["content_publisher"],
            tools=[self.wp_tool, self.li_tool],
            verbose=True,
            llm=claude_llm,
        )

    # --- Content tasks ---

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
            human_input=True,
        )

    # --- Publish task ---

    @task
    def publish_task(self) -> Task:
        return Task(config=self.tasks_config["publish_task"])

    # --- Crew ---

    @crew
    def crew(self) -> Crew:
        """
        Single sequential pipeline with HITL pause after Brand Guardian.
        Strategist → Writer → Critic → Brand Guardian [HITL] → Publisher.
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,
        )

import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "not-used"

from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, task, crew
from komet_content_intelligence.tools.proof_library import ProofLibraryTool

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
    SMOKE TEST — all agents and tasks defined for AMP auto-discovery.
    Crew only runs the Slack test. memory=False.
    """
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self, brand: str = "komet"):
        self.brand_config = load_brand_config(brand)
        self.proof_tool = ProofLibraryTool()

    # --- ALL agents must be defined for AMP ---
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
    def slack_approval_monitor(self) -> Agent:
        return Agent(
            config=self.agents_config["slack_approval_monitor"],
            verbose=True,
            llm=claude_llm,
            apps=["slack/list_channels"],
        )

    # --- ALL tasks must be defined for AMP ---
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
        )

    @task
    def slack_approval_task(self) -> Task:
        return Task(config=self.tasks_config["slack_approval_task"])

    # --- SMOKE TEST: only run the Slack task ---
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.slack_approval_monitor()],
            tasks=[self.slack_approval_task()],
            process=Process.sequential,
            verbose=True,
            memory=False,
        )

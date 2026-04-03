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
    SMOKE TEST MODE — minimal crew to verify Slack integration works.
    One agent, one task, apps=['slack'], memory=False.
    """
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self, brand: str = "komet"):
        self.brand_config = load_brand_config(brand)

    @agent
    def slack_approval_monitor(self) -> Agent:
        return Agent(
            config=self.agents_config["slack_approval_monitor"],
            verbose=True,
            llm=claude_llm,
            apps=["slack/list_channels"],
        )

    @task
    def slack_approval_task(self) -> Task:
        return Task(
            description=(
                "List all available Slack channels using the Slack tool. "
                "Return the channel names and IDs you find. "
                "This is a smoke test to verify Slack integration works."
            ),
            expected_output="List of Slack channel names and IDs.",
            agent=self.slack_approval_monitor(),
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=False,
        )

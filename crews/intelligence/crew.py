import yaml
from pathlib import Path
from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, task, crew
from dotenv import load_dotenv
from crews.intelligence.tools.web_search import WebSearchTool
from crews.intelligence.tools.gsc_metrics import GSCMetricsTool
from crews.intelligence.tools.linkedin_metrics import LinkedInMetricsTool

load_dotenv()


def load_brand_config(brand: str = "komet") -> dict:
    with open(Path(f"config/brands/{brand}.yaml")) as f:
        return yaml.safe_load(f)


@CrewBase
class IntelligenceCrew:
    """Komet Intelligence Crew — weekly autonomous research and idea generation."""
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self, brand: str = "komet"):
        self.brand_config = load_brand_config(brand)
        self.search_tool = WebSearchTool()
        self.gsc_tool = GSCMetricsTool()
        self.linkedin_tool = LinkedInMetricsTool()

    @agent
    def competitor_monitor(self) -> Agent:
        return Agent(
            config=self.agents_config["competitor_monitor"],
            tools=[self.search_tool],
            verbose=True,
            llm="claude-sonnet-4-6",
        )

    @agent
    def trend_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["trend_researcher"],
            tools=[self.search_tool],
            verbose=True,
            llm="claude-sonnet-4-6",
        )

    @agent
    def performance_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["performance_analyst"],
            tools=[self.gsc_tool, self.linkedin_tool],
            verbose=True,
            llm="claude-sonnet-4-6",
        )

    @agent
    def idea_generator(self) -> Agent:
        return Agent(
            config=self.agents_config["idea_generator"],
            verbose=True,
            llm="claude-sonnet-4-6",
        )

    @task
    def competitor_scan_task(self) -> Task:
        return Task(config=self.tasks_config["competitor_scan_task"])

    @task
    def trend_research_task(self) -> Task:
        return Task(config=self.tasks_config["trend_research_task"])

    @task
    def performance_analysis_task(self) -> Task:
        return Task(config=self.tasks_config["performance_analysis_task"])

    @task
    def idea_generation_task(self) -> Task:
        return Task(
            config=self.tasks_config["idea_generation_task"],
            output_file="outputs/weekly_ideas.md",
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

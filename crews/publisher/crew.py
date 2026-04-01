from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, task, crew
from crews.publisher.tools.wordpress_publisher import WordPressPublisherTool
from crews.publisher.tools.linkedin_publisher import LinkedInPublisherTool
from dotenv import load_dotenv

load_dotenv()


@CrewBase
class PublisherCrew:
    """
    Komet Publisher Crew.
    Runs after human approval via @human_feedback gate.
    Creates WordPress draft + LinkedIn post. Returns JSON log record.
    """
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self):
        self.wp_tool = WordPressPublisherTool()
        self.li_tool = LinkedInPublisherTool()

    @agent
    def content_publisher(self) -> Agent:
        return Agent(
            config=self.agents_config["content_publisher"],
            tools=[self.wp_tool, self.li_tool],
            verbose=True,
            llm="claude-sonnet-4-6",
        )

    @task
    def publish_task(self) -> Task:
        return Task(
            config=self.tasks_config["publish_task"],
            output_file="outputs/publish_log.json",
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

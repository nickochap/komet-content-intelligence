from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, task, crew
from dotenv import load_dotenv
from crews.creative.tools.nano_banana import NanoBananaTool
from crews.creative.tools.contentdrips import ContentdripsTool

load_dotenv()


@CrewBase
class CreativeCrew:
    """Komet Creative Crew — image and carousel generation."""
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self):
        self.image_tool = NanoBananaTool()
        self.carousel_tool = ContentdripsTool()

    @agent
    def creative_director(self) -> Agent:
        return Agent(
            config=self.agents_config["creative_director"],
            tools=[self.image_tool, self.carousel_tool],
            verbose=True,
            llm="claude-sonnet-4-6",
        )

    @task
    def creative_task(self) -> Task:
        return Task(config=self.tasks_config["creative_task"])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

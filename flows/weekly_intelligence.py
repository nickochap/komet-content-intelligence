from crewai.flow.flow import Flow, listen, start
from crews.intelligence.crew import IntelligenceCrew
from notifications.slack_notifier import SlackNotifier


class WeeklyIntelligenceFlow(Flow):
    """
    Weekly intelligence flow. Triggered by AMP cron (Monday 9AM AEST).
    Runs intelligence crew, posts each idea as a separate Slack message
    so Nick can react to individual ones to trigger content production.
    """

    @start()
    def run_intelligence(self):
        result = IntelligenceCrew().crew().kickoff()
        self.state["ideas"] = result.raw
        return result.raw

    @listen(run_intelligence)
    def post_to_slack(self, ideas: str):
        """Post each idea as its own message for individual approval."""
        notifier = SlackNotifier()
        notifier.send_ideas_list(ideas)
        return ideas

from crewai.flow.flow import Flow, listen, start
from crews.intelligence.crew import IntelligenceCrew
from notifications.slack_notifier import SlackNotifier
import os


class WeeklyIntelligenceFlow(Flow):
    """
    Weekly intelligence flow. Triggered by AMP cron (Monday 9AM AEST).
    Runs intelligence crew, posts idea list to Slack for Nick to review.
    """

    @start()
    def run_intelligence(self):
        result = IntelligenceCrew().crew().kickoff()
        self.state["ideas"] = result.raw
        return result.raw

    @listen(run_intelligence)
    def post_to_slack(self, ideas: str):
        """Post ranked idea list to Slack for Nick to approve."""
        notifier = SlackNotifier()
        notifier.send_weekly_summary({
            "ideas_count": ideas.count("##"),
            "competitors_scanned": 5,
            "trends_count": 7,
        })
        return ideas

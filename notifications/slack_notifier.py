import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackNotifier:
    def __init__(self):
        self.client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
        self.content_channel = os.getenv("SLACK_CONTENT_CHANNEL", "C0AHAK5CMFB")
        self.caden_channel = os.getenv("SLACK_CADEN_CHANNEL", "C0AGGM4225D")

    def send_content_for_approval(self, content_pack: str, topic: str, qa_scores: dict) -> bool:
        """Gate 1 — Nick approves content quality"""
        avg = sum(qa_scores.values()) / len(qa_scores) if qa_scores else 0
        try:
            self.client.chat_postMessage(
                channel=self.content_channel,
                text=(
                    f":memo: *Content ready for approval*\n\n"
                    f"*Topic:* {topic}\n"
                    f"*QA Average:* {avg:.1f}/5.0\n\n"
                    f"{content_pack[:2000]}\n\n"
                    f"React :white_check_mark: to approve, :x: to reject, :arrows_counterclockwise: to request revision."
                ),
                mrkdwn=True,
            )
            return True
        except SlackApiError as e:
            print(f"Slack error: {e}")
            return False

    def send_agentforce_for_caden_review(self, content_pack: str, topic: str, reason: str) -> bool:
        """Agentforce technical review — Caden approves before Gate 2"""
        try:
            self.client.chat_postMessage(
                channel=self.caden_channel,
                text=(
                    f":robot_face: *Agentforce content — technical review required*\n\n"
                    f"*Topic:* {topic}\n"
                    f"*Review reason:* {reason}\n\n"
                    f"Please review all Agentforce capability claims for technical accuracy "
                    f"against current Salesforce documentation.\n\n"
                    f"{content_pack[:2000]}\n\n"
                    f"React :white_check_mark: to approve technical accuracy, :x: if claims need correction."
                ),
                mrkdwn=True,
            )
            return True
        except SlackApiError as e:
            print(f"Slack error (Caden channel): {e}")
            return False

    def send_error_alert(self, error_message: str, node: str = "Unknown") -> None:
        """Error alert — matches existing n8n error format"""
        try:
            self.client.chat_postMessage(
                channel=self.content_channel,
                text=(
                    f":red_circle: *Content Pipeline Error*\n"
                    f"Node: {node}\n"
                    f"Error: {error_message}\n"
                    f"Action required: check and restart manually."
                ),
                mrkdwn=True,
            )
        except SlackApiError:
            pass  # Don't raise on notification failure

    def send_weekly_summary(self, metrics: dict) -> None:
        """Weekly metrics summary — matches existing n8n format"""
        try:
            self.client.chat_postMessage(
                channel=self.content_channel,
                text=(
                    f":bar_chart: *Weekly Intelligence Summary*\n\n"
                    f"Ideas generated: {metrics.get('ideas_count', 0)}\n"
                    f"Competitors scanned: {metrics.get('competitors_scanned', 0)}\n"
                    f"Trend topics identified: {metrics.get('trends_count', 0)}\n\n"
                    f"Idea list ready for review in Slack."
                ),
                mrkdwn=True,
            )
        except SlackApiError:
            pass

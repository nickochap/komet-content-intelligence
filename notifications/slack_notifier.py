import os
import re
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackNotifier:
    def __init__(self):
        self.client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
        self.content_channel = os.getenv("SLACK_CONTENT_CHANNEL", "C0AHAK5CMFB")

    def send_ideas_list(self, ideas_raw: str) -> None:
        """Post each idea as its own Slack message so Nick can react to trigger production."""
        ideas = self._parse_ideas(ideas_raw)
        if not ideas:
            self._post(
                f":bulb: *Weekly Intelligence Report*\n\n{ideas_raw[:2000]}"
            )
            return

        self._post(
            f":bar_chart: *Weekly Intelligence — {len(ideas)} ideas ranked*\n"
            f"React :white_check_mark: on any idea to start content production."
        )
        for i, idea in enumerate(ideas, 1):
            self._post(
                f":bulb: *Idea {i}:* {idea[:500]}\n"
                f"React :white_check_mark: to produce this one."
            )

    def send_content_for_approval(self, content_pack: str, topic: str, qa_scores: dict) -> bool:
        """Post content for Nick's review — used alongside @human_feedback."""
        avg = sum(qa_scores.values()) / len(qa_scores) if qa_scores else 0
        try:
            self.client.chat_postMessage(
                channel=self.content_channel,
                text=(
                    f":memo: *Content ready for approval*\n\n"
                    f"*Topic:* {topic}\n"
                    f"*QA Average:* {avg:.1f}/5.0\n\n"
                    f"{content_pack[:2000]}\n\n"
                    f"React :white_check_mark: to approve, :x: to reject, "
                    f":arrows_counterclockwise: to request revision."
                ),
                mrkdwn=True,
            )
            return True
        except SlackApiError as e:
            print(f"Slack error: {e}")
            return False

    def send_publish_complete(self, topic: str, wp_url: str, linkedin_url: str) -> None:
        """Final notification — draft ready for visual review in WordPress."""
        parts = [f":rocket: *Content published*\n\n*Topic:* {topic}"]
        if wp_url:
            parts.append(f":wordpress: *WordPress draft:* {wp_url}")
        if linkedin_url:
            parts.append(f":linkedin: *LinkedIn post:* {linkedin_url}")
        parts.append("\nReview the WordPress draft and hit Publish when ready.")
        self._post("\n".join(parts))

    def send_error_alert(self, error_message: str, node: str = "Unknown") -> None:
        """Error alert to content channel."""
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
            pass

    def _post(self, text: str) -> None:
        """Helper — post to content channel, swallow errors."""
        try:
            self.client.chat_postMessage(
                channel=self.content_channel,
                text=text,
                mrkdwn=True,
            )
        except SlackApiError as e:
            print(f"Slack error: {e}")

    @staticmethod
    def _parse_ideas(raw: str) -> list[str]:
        """Split numbered ideas from intelligence crew output."""
        lines = raw.strip().split("\n")
        ideas = []
        current = []
        for line in lines:
            if re.match(r"^\s*\d+[\.\)]\s", line):
                if current:
                    ideas.append("\n".join(current).strip())
                current = [line]
            elif current:
                current.append(line)
        if current:
            ideas.append("\n".join(current).strip())
        return ideas

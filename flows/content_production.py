from pydantic import BaseModel
from typing import Optional
from crewai.flow.flow import Flow, start, listen, or_
from crewai.flow.persistence import persist
from crewai.flow.human_feedback import human_feedback
from crewai.flow.async_feedback.types import HumanFeedbackResult
from crews.content.crew import ContentCrew
from crews.creative.crew import CreativeCrew
from crews.publisher.crew import PublisherCrew
from notifications.slack_notifier import SlackNotifier
import json


class ContentProductionState(BaseModel):
    """Typed, SQLite-backed state — full fidelity between crews."""
    id: Optional[str] = None
    topic: str = ""
    content_brief: str = ""
    content_pack: str = ""
    qa_scores: dict = {}
    creative_assets: str = ""
    publish_urls: dict = {}
    content_type: str = "both"
    revision_count: int = 0


@persist
class ContentProductionFlow(Flow[ContentProductionState]):
    """
    Single flow with native persistence and human approval gates.
    Content → [Nick approves] → Creative → [Nick approves] → Publish.
    All data stays in self.state (SQLite-backed). No webhooks, no truncation.
    """

    @start()
    def receive_brief(self):
        """Entry point — receives idea from AMP Slack trigger."""
        return self.state.content_brief

    @human_feedback(
        message=(
            "Content is ready for review.\n"
            "Reply 'approved' to proceed to image generation,\n"
            "'rejected' to stop, or describe what needs revision."
        ),
        emit=["content_approved", "content_rejected", "content_needs_revision"],
        llm="claude-sonnet-4-6",
        default_outcome="content_needs_revision",
    )
    @listen(or_("receive_brief", "content_needs_revision"))
    def run_content_crew(self):
        """Run the 4-agent content crew. Loops back here on revision."""
        self.state.revision_count += 1
        result = ContentCrew().crew().kickoff(
            inputs={"content_brief": self.state.content_brief}
        )
        self.state.content_pack = result.raw
        return self.state.content_pack

    @listen("content_rejected")
    def handle_content_rejection(self, result: HumanFeedbackResult):
        """Nick rejected the content — notify and stop."""
        notifier = SlackNotifier()
        notifier.send_error_alert(
            f"Content rejected by Nick: {result.feedback}",
            node="ContentProductionFlow",
        )

    @human_feedback(
        message=(
            "Creative assets are ready for review.\n"
            "Reply 'approved' to publish, or 'rejected' to regenerate images."
        ),
        emit=["creative_approved", "creative_rejected"],
        llm="claude-sonnet-4-6",
        default_outcome="creative_rejected",
    )
    @listen("content_approved")
    def run_creative_crew(self, result: HumanFeedbackResult = None):
        """Generate images using the approved content pack."""
        creative_result = CreativeCrew().crew().kickoff(
            inputs={"content_pack": self.state.content_pack}
        )
        self.state.creative_assets = creative_result.raw
        return self.state.creative_assets

    @listen("creative_rejected")
    def retry_creative(self, result: HumanFeedbackResult):
        """Re-run creative only — content stays as-is."""
        creative_result = CreativeCrew().crew().kickoff(
            inputs={"content_pack": self.state.content_pack}
        )
        self.state.creative_assets = creative_result.raw

    @listen("creative_approved")
    def run_publisher(self, result: HumanFeedbackResult):
        """Publish using full content_pack + creative_assets from state."""
        pub_result = PublisherCrew().crew().kickoff(
            inputs={
                "content_pack": self.state.content_pack,
                "creative_asset": self.state.creative_assets,
                "content_type": self.state.content_type,
            }
        )
        try:
            self.state.publish_urls = json.loads(pub_result.raw)
        except (json.JSONDecodeError, TypeError):
            self.state.publish_urls = {"raw": pub_result.raw[:500]}

    @listen(run_publisher)
    def notify_complete(self):
        """Send final Slack notification with draft URLs."""
        notifier = SlackNotifier()
        notifier.send_publish_complete(
            topic=self.state.topic,
            wp_url=self.state.publish_urls.get("wordpress_draft_url", ""),
            linkedin_url=self.state.publish_urls.get("linkedin_url", ""),
        )

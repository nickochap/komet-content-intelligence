from crewai.flow.flow import Flow, listen, start, and_
from crews.content.crew import ContentCrew
from crews.creative.crew import CreativeCrew
from crews.publisher.crew import PublisherCrew
import json, requests, os


class ContentProductionFlow(Flow):
    """
    Full production flow. Triggered by AMP Slack trigger.
    Content + Creative run in parallel.
    Publisher runs after AMP HITL approval.
    Sends tiny log JSON to n8n for Google Sheets only.
    """

    @start()
    def receive_brief(self, crewai_trigger_payload: dict = None):
        if crewai_trigger_payload:
            brief = crewai_trigger_payload.get("text", "")
            self.state["content_brief"] = brief
            self.state["topic"] = crewai_trigger_payload.get("topic", brief[:80])
        return self.state.get("content_brief", "")

    @listen(receive_brief)
    def run_content_crew(self, brief: str):
        result = ContentCrew().crew().kickoff(inputs={"content_brief": brief})
        self.state["content_result"] = result.raw
        return result.raw

    @listen(receive_brief)
    def run_creative_crew(self, brief: str):
        result = CreativeCrew().crew().kickoff(inputs={"content_brief": brief})
        self.state["creative_result"] = result.raw
        return result.raw

    @listen(and_(run_content_crew, run_creative_crew))
    def prepare_for_approval(self, *args):
        """AMP HITL pauses here — Nick approves everything in one gate."""
        return {
            "content": self.state.get("content_result", ""),
            "creative": self.state.get("creative_result", ""),
            "topic": self.state.get("topic", "")
        }

    @listen(prepare_for_approval)
    def run_publisher(self, approved_pack: dict):
        """After HITL approval — Publisher handles WordPress MCP + LinkedIn API directly."""
        result = PublisherCrew().crew().kickoff(inputs={
            "content_pack": approved_pack.get("content", ""),
            "creative_asset": approved_pack.get("creative", ""),
            "content_type": self.state.get("content_type", "both")
        })
        try:
            log_record = json.loads(result.raw)
        except Exception:
            log_record = {"raw": result.raw[:500]}
        self.state["log_record"] = log_record
        return log_record

    @listen(run_publisher)
    def send_log_to_n8n(self, log_record: dict):
        """Tiny JSON log to n8n — just metadata + URLs. No content in payload."""
        webhook = os.getenv("N8N_LOG_WEBHOOK_URL")
        if webhook:
            requests.post(webhook, json=log_record, timeout=10)
        return log_record

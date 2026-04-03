"""
Slack posting tool for the Publisher agent.
Posts LinkedIn content text to Slack for Nick to copy-paste.
Uses slack_sdk directly (same approach as the guardrail).
"""

import os
from crewai.tools import BaseTool
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackPosterTool(BaseTool):
    name: str = "Slack Poster"
    description: str = """
    Post content to the Komet Slack content channel.
    Use this to post LinkedIn post text for Nick to copy-paste to LinkedIn.
    Input: message text to post. Can include markdown formatting.
    Optionally post follow-up comments as thread replies by providing
    thread_replies as a comma-separated list of messages.
    Returns: confirmation with message timestamp.
    """

    def _run(self, message: str, thread_replies: str = "") -> str:
        token = os.getenv("SLACK_BOT_TOKEN", "")
        raw_channel = os.getenv("SLACK_CONTENT_CHANNEL", "C0AHAK5CMFB")
        channel = raw_channel.split("#")[0].split()[0].strip()

        if not token:
            return "Slack error: No SLACK_BOT_TOKEN configured."

        client = WebClient(token=token)

        try:
            # Post the main message
            result = client.chat_postMessage(
                channel=channel,
                text=message,
                mrkdwn=True,
            )
            msg_ts = result["ts"]

            # Post thread replies if provided
            if thread_replies.strip():
                replies = [r.strip() for r in thread_replies.split("|||") if r.strip()]
                for reply in replies:
                    client.chat_postMessage(
                        channel=channel,
                        thread_ts=msg_ts,
                        text=reply,
                        mrkdwn=True,
                    )

            return f"Posted to Slack (ts: {msg_ts}). {len(replies) if thread_replies.strip() else 0} thread replies posted."

        except SlackApiError as e:
            return f"Slack error: {e.response['error']}"
        except Exception as e:
            return f"Slack error: {str(e)[:200]}"

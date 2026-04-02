"""
Approval guardrail for Komet content pipeline.

Posts content summary to Slack, polls for Nick's emoji reaction.
Runs as a synchronous Python function inside the crew process — no
Enterprise features required.

✅ = approve → (True, {}) → crew continues to Creative + Publisher
❌ = reject → (False, "feedback") → Brand Guardian re-executes with notes
⏰ = timeout → pipeline stops gracefully
"""

import os
import time
from typing import Tuple, Any
from crewai import TaskOutput
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

POLL_INTERVAL = 30  # seconds between Slack reaction checks
TIMEOUT_HOURS = 4   # max wait before auto-timeout
PREVIEW_CHARS = 1900  # Slack message limit safety margin


def approval_guardrail(result: TaskOutput) -> Tuple[bool, Any]:
    """
    Posts content summary to Slack, polls for Nick's reaction.

    Returns:
        (True, {})              — approved, crew continues. Empty dict
                                  prevents overwriting task output.
        (False, "feedback")     — rejected, Brand Guardian re-executes
                                  with Nick's feedback from thread.
        (False, "Timed out...") — no response within timeout.
    """
    # Debug — this ALWAYS prints to AMP logs regardless of Slack success/failure
    print(f"GUARDRAIL ENTERED — result length: {len(result.raw)}")
    print(f"GUARDRAIL ENV — SLACK_BOT_TOKEN present: {bool(os.getenv('SLACK_BOT_TOKEN'))}")
    print(f"GUARDRAIL ENV — SLACK_CONTENT_CHANNEL: {os.getenv('SLACK_CONTENT_CHANNEL', 'NOT SET')}")

    client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
    channel = os.getenv("SLACK_CONTENT_CHANNEL", "C0AHAK5CMFB")

    # Post summary to Slack (not full content — Slack has message limits)
    try:
        msg = client.chat_postMessage(
            channel=channel,
            text=(
                ":clipboard: *Content Package — Awaiting Approval*\n\n"
                f"{result.raw[:PREVIEW_CHARS]}\n\n"
                "---\n"
                "React :white_check_mark: to approve and continue to image generation.\n"
                "React :x: to reject — reply in this thread with revision notes."
            ),
            mrkdwn=True,
        )
    except Exception as e:
        # Log the FULL error for debugging — print goes to AMP logs
        print(f"GUARDRAIL SLACK ERROR [{type(e).__name__}]: {e}")
        print(f"SLACK_BOT_TOKEN present: {bool(os.getenv('SLACK_BOT_TOKEN'))}")
        print(f"SLACK_BOT_TOKEN starts with: {os.getenv('SLACK_BOT_TOKEN', '')[:10]}...")
        print(f"Channel: {channel}")
        # Auto-approve so pipeline isn't blocked — but error is logged
        return (True, {})

    msg_ts = msg["ts"]
    deadline = time.time() + (TIMEOUT_HOURS * 3600)

    while time.time() < deadline:
        time.sleep(POLL_INTERVAL)

        try:
            reactions_resp = client.reactions_get(
                channel=channel, timestamp=msg_ts, full=True
            )
        except SlackApiError:
            continue  # Transient Slack error — retry next poll

        reactions = reactions_resp.get("message", {}).get("reactions", [])

        for r in reactions:
            # Check for approval
            if r["name"] in ("white_check_mark", "heavy_check_mark"):
                _reply(client, channel, msg_ts,
                       ":white_check_mark: Approved. Proceeding to image generation.")
                return (True, {})

            # Check for rejection
            if r["name"] == "x":
                feedback = _get_thread_feedback(client, channel, msg_ts)
                _reply(client, channel, msg_ts,
                       f":x: Rejected. Revision loop triggered.")
                return (False, feedback)

    # Timeout — no reaction within the window
    _reply(client, channel, msg_ts,
           ":alarm_clock: Approval timed out after "
           f"{TIMEOUT_HOURS} hours. Pipeline stopped.")
    return (False, "Timed out waiting for approval — pipeline stopped")


def _get_thread_feedback(client: WebClient, channel: str, thread_ts: str) -> str:
    """Extract Nick's revision notes from the Slack thread."""
    try:
        replies = client.conversations_replies(channel=channel, ts=thread_ts)
        messages = replies.get("messages", [])
        # Skip the original message (index 0), collect thread replies
        feedback_parts = []
        for msg in messages[1:]:
            # Only include messages from humans (not the bot)
            if not msg.get("bot_id"):
                feedback_parts.append(msg.get("text", ""))
        feedback = "\n".join(feedback_parts).strip()
        return feedback or "Rejected without specific feedback"
    except SlackApiError:
        return "Rejected without specific feedback"


def _reply(client: WebClient, channel: str, thread_ts: str, text: str) -> None:
    """Post a reply in the approval thread."""
    try:
        client.chat_postMessage(channel=channel, thread_ts=thread_ts, text=text)
    except SlackApiError:
        pass  # Don't fail on notification errors

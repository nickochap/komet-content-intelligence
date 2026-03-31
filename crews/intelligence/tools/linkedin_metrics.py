import os
import requests
from crewai.tools import BaseTool


class LinkedInMetricsTool(BaseTool):
    name: str = "LinkedIn Metrics"
    description: str = """
    Fetch recent LinkedIn page metrics for the Komet company page.
    Returns engagement data: impressions, clicks, reactions, comments
    for recent posts. Use to analyse content performance.
    """

    def _run(self, days_back: int = 7) -> str:
        access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        org_id = os.getenv("LINKEDIN_ORG_ID")

        headers = {
            "Authorization": f"Bearer {access_token}",
            "LinkedIn-Version": "202402",
            "X-Restli-Protocol-Version": "2.0.0",
        }

        response = requests.get(
            f"https://api.linkedin.com/rest/organizationalEntityShareStatistics"
            f"?q=organizationalEntity&organizationalEntity=urn:li:organization:{org_id}",
            headers=headers,
        )

        if response.status_code != 200:
            return f"LinkedIn API error {response.status_code}: {response.text[:300]}"

        data = response.json()
        elements = data.get("elements", [])

        if not elements:
            return "No LinkedIn metrics available for this period."

        stats = elements[0].get("totalShareStatistics", {})
        summary = [
            "LinkedIn Page Metrics (recent period):",
            f"Impressions: {stats.get('impressionCount', 0)}",
            f"Clicks: {stats.get('clickCount', 0)}",
            f"Reactions: {stats.get('likeCount', 0)}",
            f"Comments: {stats.get('commentCount', 0)}",
            f"Shares: {stats.get('shareCount', 0)}",
            f"Engagement rate: {stats.get('engagement', 0):.4f}",
        ]

        return "\n".join(summary)

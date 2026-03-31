import os
import requests
from google.oauth2.service_account import Credentials
from crewai.tools import BaseTool


class GSCMetricsTool(BaseTool):
    name: str = "Google Search Console Metrics"
    description: str = "Fetch recent GSC metrics for gokomet.com — clicks, impressions, position by page and query"

    def _run(self, days_back: int = 7) -> str:
        """
        Uses same Google OAuth credential as n8n (Google account - Komet Search API).
        Credential JSON path set in GOOGLE_SHEETS_CREDENTIALS_PATH.
        """
        from datetime import datetime, timedelta
        import json

        creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
        site_url = os.getenv("GSC_SITE_URL", "sc-domain:gokomet.com")

        with open(creds_path) as f:
            cred_data = json.load(f)

        creds = Credentials.from_service_account_info(
            cred_data,
            scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
        )

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

        response = requests.post(
            f"https://www.googleapis.com/webmasters/v3/sites/{site_url.replace(':', '%3A')}/searchAnalytics/query",
            headers={"Authorization": f"Bearer {creds.token}"},
            json={
                "startDate": start_date,
                "endDate": end_date,
                "dimensions": ["page", "query"],
                "rowLimit": 100
            }
        )

        data = response.json()
        rows = data.get("rows", [])

        if not rows:
            return "No GSC data available for this period."

        top_pages = sorted(rows, key=lambda r: r.get("clicks", 0), reverse=True)[:10]
        summary = ["Top performing pages (last 7 days):"]
        for row in top_pages:
            page = row.get("keys", [""])[0]
            query = row.get("keys", ["", ""])[1] if len(row.get("keys", [])) > 1 else ""
            summary.append(
                f"Page: {page} | Query: {query} | "
                f"Clicks: {row.get('clicks', 0)} | "
                f"Position: {row.get('position', 0):.1f}"
            )

        return "\n".join(summary)

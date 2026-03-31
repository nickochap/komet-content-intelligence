import os
import gspread
from google.oauth2.service_account import Credentials
from crewai.tools import BaseTool


class ProofLibraryTool(BaseTool):
    name: str = "Proof Library"
    description: str = """
    Retrieves proof items from the Komet proof library by ID.
    Use to fetch specific micro-stories (MS-01 through MS-12) or
    patterns (P-01 through P-10). Returns claimable and background
    fields. Only use claimable content in published posts.
    Input: comma-separated proof IDs e.g. "MS-01, MS-03, P-02"
    """

    def _run(self, proof_ids: str) -> str:
        creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
        sheet_id = os.getenv("GOOGLE_SHEETS_ID")

        scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(sheet_id).worksheet("Proof Library")
        records = sheet.get_all_records()

        requested_ids = [pid.strip() for pid in proof_ids.split(",")]
        results = []

        for record in records:
            proof_id = record.get("ID", "")
            if proof_id in requested_ids:
                results.append(
                    f"ID: {proof_id}\n"
                    f"Type: {record.get('Type', '')}\n"
                    f"CLAIMABLE: {record.get('Claimable', '')}\n"
                    f"BACKGROUND ONLY: {record.get('Background', '')}\n"
                    f"Anonymisation: {record.get('Anonymisation Level', '')}\n"
                    "---"
                )

        if not results:
            return f"No proof items found for IDs: {proof_ids}"

        return "\n".join(results)

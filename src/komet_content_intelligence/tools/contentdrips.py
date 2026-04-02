import os
import requests
from crewai.tools import BaseTool


class ContentdripsTool(BaseTool):
    name: str = "Carousel Generator"
    description: str = """
    Generate a LinkedIn PDF carousel via Contentdrips API.
    Input: JSON list of slides, each with 'heading' and 'description'.
    Returns PDF URL for LinkedIn document upload.
    Example input: [{"heading": "Why most Salesforce projects fail", "description": "The lifecycle was never defined."}, ...]
    """

    def _run(self, slides_json: str) -> str:
        import json
        api_key = os.getenv("CONTENTDRIPS_API_KEY")
        template_id = os.getenv("CONTENTDRIPS_TEMPLATE_ID")

        try:
            slides = json.loads(slides_json) if isinstance(slides_json, str) else slides_json
        except json.JSONDecodeError:
            return "Error: slides_json must be valid JSON"

        response = requests.post(
            "https://api.contentdrips.com/v1/generate",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"template_id": template_id, "output_format": "pdf", "slides": slides}
        )

        if response.status_code != 200:
            return f"Contentdrips error {response.status_code}: {response.text[:200]}"

        result = response.json()
        export_urls = result.get("export_url", [])
        pdf_url = export_urls[0] if isinstance(export_urls, list) and export_urls else result.get("export_url", "")
        return pdf_url or "Carousel generation failed — check template ID and API key"

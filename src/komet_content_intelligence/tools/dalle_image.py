"""
DALL-E image generation tool for Komet content pipeline.
Uses OpenAI's DALL-E 3 API to generate professional B2B images
from the IMAGE BRIEF section of approved content packages.
"""

import os
from crewai.tools import BaseTool
from openai import OpenAI


class DalleImageTool(BaseTool):
    name: str = "Image Generator"
    description: str = """
    Generate a professional B2B image using DALL-E 3.
    Input: image description (text prompt describing what to generate).
    Optional: format parameter — 'blog' for 1792x1024 landscape, 'linkedin' for 1024x1024 square.
    Default: linkedin (square).
    Returns: image URL.
    """

    def _run(self, prompt: str, format: str = "linkedin") -> str:
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key or api_key == "not-used":
            return "DALL-E error: No valid OPENAI_API_KEY configured. Set a real OpenAI API key."

        # Select size based on content format
        if format.lower() in ("blog", "blog_article", "landscape", "hero"):
            size = "1792x1024"
        else:
            size = "1024x1024"

        # Prepend Komet brand direction to every prompt
        brand_prompt = (
            "Professional B2B graphic for an Australian Salesforce consultancy. "
            "Dark navy background (#0B1A2B). Teal accent (#1D9E75). "
            "Clean, authoritative, minimal. No people, no stock photography, "
            "no lifestyle imagery. Bold sans-serif text if text is included. "
            "The style should feel like a statement, not a slide deck. "
            f"\n\n{prompt}"
        )

        try:
            client = OpenAI(api_key=api_key)
            response = client.images.generate(
                model="dall-e-3",
                prompt=brand_prompt,
                size=size,
                quality="hd",
                n=1,
            )
            image_url = response.data[0].url
            return f"IMAGE_URL: {image_url}"
        except Exception as e:
            return f"DALL-E error: {str(e)[:300]}"

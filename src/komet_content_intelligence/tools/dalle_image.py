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
        # Try multiple env var names — AMP may set OPENAI_API_KEY after our import
        dalle_key = os.getenv("DALLE_API_KEY", "")
        openai_key = os.getenv("OPENAI_API_KEY", "")

        # Pick the first valid key (not empty, not 'not-used')
        api_key = ""
        for k in [dalle_key, openai_key]:
            if k and k != "not-used" and k.startswith("sk-"):
                api_key = k
                break

        print(f"DALL-E — DALLE_API_KEY present: {bool(dalle_key)} starts: {dalle_key[:10]}...")
        print(f"DALL-E — OPENAI_API_KEY present: {bool(openai_key)} starts: {openai_key[:10]}...")
        print(f"DALL-E — selected key starts: {api_key[:10]}...")

        if not api_key:
            return (
                f"DALL-E error: No valid API key. "
                f"DALLE_API_KEY={dalle_key[:8]}... OPENAI_API_KEY={openai_key[:8]}... "
                f"Set a real OpenAI key (starting with sk-) in AMP Environment Variables."
            )

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

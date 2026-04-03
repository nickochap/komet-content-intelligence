"""
Nano Banana 2 image generation tool for Komet content pipeline.
Uses Google's Gemini API (Nano Banana 2 = gemini-2.0-flash-exp)
with brand system instructions for consistent Komet visual identity.

System instruction loaded from config/brands/komet.yaml ensures
every generated image matches Komet's visual identity.
"""

import os
import base64
import yaml
from pathlib import Path
from io import BytesIO
from crewai.tools import BaseTool


def _load_brand_visual_prompt() -> str:
    """Load visual identity rules from brand config as system instruction."""
    for base in [Path(__file__).parent.parent.parent.parent, Path.cwd()]:
        path = base / "config" / "brands" / "komet.yaml"
        if path.exists():
            with open(path) as f:
                brand = yaml.safe_load(f)
            vi = brand.get("visual_identity", {})
            palette = vi.get("palette", {})
            return (
                "You generate professional B2B marketing visuals for Komet "
                "(gokomet.com), an Australian Salesforce consultancy targeting "
                "AU/NZ education providers.\n"
                f"Primary colour: {palette.get('primary', 'dark navy #0B1A2B')}\n"
                f"Accent colour: {palette.get('accent', 'teal #1D9E75')}\n"
                f"Background: {palette.get('background', 'white #F4F6F8')}\n"
                "Style: clean, modern, geometric flat design. Professional B2B.\n"
                "Typography: bold sans-serif headings, high contrast.\n"
                "Never cartoonish. Always corporate-professional.\n"
                "No stock photography of people. No aspirational lifestyle imagery.\n"
                "Include 'gokomet.com' as text in a CTA bar or footer area.\n"
                "Prefer process diagrams, data visualisations, split-panel "
                "before/after layouts, infographic-style content.\n"
            )
    return (
        "You generate professional B2B marketing visuals for Komet (gokomet.com). "
        "Dark navy (#0B1A2B) and teal (#1D9E75). Clean, modern, corporate. "
        "Include gokomet.com text. No people, no stock photography."
    )


class NanoBananaTool(BaseTool):
    name: str = "Image Generator"
    description: str = """
    Generate a professional B2B infographic image for Komet content using Nano Banana 2.
    Input: the full content text (LinkedIn post or blog excerpt) that the image
    should accompany. The tool reads the content and produces a matching visual.
    Brand styling is applied automatically via system instructions.
    Optional: format parameter — 'linkedin' for 4:5, 'blog' for 16:9.
    Returns: path to the generated image file.
    """

    def _run(self, prompt: str, format: str = "linkedin") -> str:
        api_key = os.getenv("NANO_BANANA_API_KEY", "")

        if not api_key:
            return "Image generation error: No NANO_BANANA_API_KEY configured in environment."

        try:
            from google import genai
            from google.genai import types
        except ImportError:
            return "Image generation error: google-genai package not installed. Add 'google-genai' to dependencies."

        # Select aspect ratio
        if format.lower() in ("blog", "blog_article", "landscape", "hero"):
            aspect_ratio = "16:9"
        else:
            aspect_ratio = "4:5"

        brand_system = _load_brand_visual_prompt()

        try:
            client = genai.Client(api_key=api_key)

            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=[
                    f"Create a professional LinkedIn infographic image for this content. "
                    f"Make it visually compelling for B2B education decision-makers. "
                    f"Include key points as clean text overlays in the image. "
                    f"Include 'gokomet.com' and a call-to-action in a footer bar.\n\n"
                    f"CONTENT:\n{prompt}"
                ],
                config=types.GenerateContentConfig(
                    system_instruction=brand_system,
                    response_modalities=["TEXT", "IMAGE"],
                ),
            )

            # Extract image from response
            for part in response.candidates[0].content.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    img_data = part.inline_data.data
                    img_path = Path("outputs") / "generated_image.png"
                    img_path.parent.mkdir(exist_ok=True)
                    with open(img_path, "wb") as f:
                        f.write(img_data)
                    return f"IMAGE_GENERATED: {img_path}"

            # Check for text-only response
            text_parts = [p.text for p in response.candidates[0].content.parts if hasattr(p, "text")]
            if text_parts:
                return f"Image generation returned text only (no image): {text_parts[0][:200]}"

            return "Image generation completed but no image was returned."

        except Exception as e:
            return f"Image generation error: {str(e)[:400]}"

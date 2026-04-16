"""
Nano Banana 2 image generation tool for Komet content pipeline.
Uses Google's Gemini API via REST (no google-genai dependency needed).
Brand system instructions loaded from komet.yaml for consistent visual identity.
"""

import os
import base64
import json
import yaml
import requests
from pathlib import Path
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
    Optional: format parameter — 'linkedin' for square, 'blog' for landscape.
    Returns: path to the generated image file.
    """

    def _run(self, prompt: str, format: str = "linkedin") -> str:
        api_key = os.getenv("NANO_BANANA_API_KEY", "")

        if not api_key:
            return "Image generation error: No NANO_BANANA_API_KEY configured."

        brand_system = _load_brand_visual_prompt()

        content_prompt = (
            "Create a professional LinkedIn infographic image for this content. "
            "Make it visually compelling for B2B education decision-makers. "
            "Include key points as clean text overlays in the image. "
            "Include 'gokomet.com' and a call-to-action in a footer bar.\n\n"
            f"CONTENT:\n{prompt}"
        )

        # Use Gemini REST API directly — no google-genai dependency needed
        # gemini-3.1-flash-image-preview is Nano Banana 2 (requires billing enabled)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-image-preview:generateContent?key={api_key}"

        payload = {
            "system_instruction": {
                "parts": [{"text": brand_system}]
            },
            "contents": [
                {
                    "parts": [{"text": content_prompt}]
                }
            ],
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"],
            }
        }

        try:
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=60,
            )

            if response.status_code != 200:
                return f"Image generation error (HTTP {response.status_code}): {response.text[:300]}"

            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                return "Image generation error: No candidates in response."

            parts = candidates[0].get("content", {}).get("parts", [])

            for part in parts:
                if "inlineData" in part:
                    img_b64 = part["inlineData"]["data"]
                    img_bytes = base64.b64decode(img_b64)

                    img_path = Path("outputs") / "generated_image.png"
                    img_path.parent.mkdir(exist_ok=True)
                    with open(img_path, "wb") as f:
                        f.write(img_bytes)

                    return f"IMAGE_GENERATED: {img_path}"

            # No image in response — check for text
            text_parts = [p.get("text", "") for p in parts if "text" in p]
            if text_parts:
                return f"Image generation returned text only: {text_parts[0][:200]}"

            return "Image generation completed but no image in response."

        except requests.Timeout:
            return "Image generation error: Request timed out (60s limit)."
        except Exception as e:
            return f"Image generation error: {str(e)[:300]}"

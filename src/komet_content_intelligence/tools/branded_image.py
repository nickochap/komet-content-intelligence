"""
Combined image generation + logo overlay tool.

Single tool that calls Nano Banana 2 and applies the Komet logo,
with result_as_answer=True so the CrewAI agent cannot skip it or
hallucinate fake output.
"""

import os
import base64
import yaml
import requests
from pathlib import Path
from crewai.tools import BaseTool
from PIL import Image


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
        "Dark navy (#0B1A2B) and teal (#1D9E75). Clean, modern, corporate."
    )


def _find_logo() -> str:
    """Find the Komet logo PNG in config/brands/."""
    for base in [Path(__file__).parent.parent.parent.parent, Path.cwd()]:
        for name in ["komet_logo.png", "logo.png", "komet-logo.png"]:
            path = base / "config" / "brands" / name
            if path.exists():
                return str(path)
    return ""


class BrandedImageTool(BaseTool):
    name: str = "Generate Branded Image"
    description: str = (
        "Generate a professional Komet-branded image for the content package. "
        "Input: the full content text (FINAL POST or ARTICLE). "
        "Optional: format='linkedin' (default) or 'blog'. "
        "This single tool calls Nano Banana 2 AND applies the Komet logo. "
        "Returns the path to the final branded image, or an error message."
    )
    result_as_answer: bool = True  # Force CrewAI to use this output as the final answer

    def _run(self, prompt: str, format: str = "linkedin") -> str:
        # Step 1: Nano Banana 2 via REST API
        api_key = os.getenv("NANO_BANANA_API_KEY", "")
        if not api_key:
            return "ERROR: No NANO_BANANA_API_KEY configured in AMP Environment Variables."

        brand_system = _load_brand_visual_prompt()
        content_prompt = (
            "Create a professional LinkedIn infographic image for this content. "
            "Make it visually compelling for B2B education decision-makers. "
            "Include key points as clean text overlays in the image. "
            "Include 'gokomet.com' and a call-to-action in a footer bar.\n\n"
            f"CONTENT:\n{prompt}"
        )

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-3.1-flash-image-preview:generateContent?key={api_key}"
        )
        payload = {
            "system_instruction": {"parts": [{"text": brand_system}]},
            "contents": [{"parts": [{"text": content_prompt}]}],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
        }

        try:
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=120,
            )
        except Exception as e:
            return f"ERROR: Nano Banana HTTP request failed — {str(e)[:200]}"

        if response.status_code != 200:
            return f"ERROR: Nano Banana HTTP {response.status_code} — {response.text[:300]}"

        try:
            data = response.json()
        except Exception as e:
            return f"ERROR: Nano Banana response not JSON — {str(e)[:200]}"

        candidates = data.get("candidates", [])
        if not candidates:
            return f"ERROR: Nano Banana returned no candidates — {str(data)[:300]}"

        # Extract image
        img_bytes = None
        for part in candidates[0].get("content", {}).get("parts", []):
            if "inlineData" in part:
                img_bytes = base64.b64decode(part["inlineData"]["data"])
                break

        if not img_bytes:
            return f"ERROR: Nano Banana returned no image data — response: {str(data)[:400]}"

        # Save generated image
        generated_path = Path("outputs") / "generated_image.png"
        generated_path.parent.mkdir(exist_ok=True)
        with open(generated_path, "wb") as f:
            f.write(img_bytes)

        # Step 2: Apply logo overlay
        logo_path = _find_logo()
        if not logo_path:
            return (
                f"IMAGE_GENERATED (no logo overlay — logo file not found): "
                f"{generated_path}"
            )

        try:
            base = Image.open(generated_path).convert("RGBA")
            logo = Image.open(logo_path).convert("RGBA")

            width, height = base.size
            logo_width = int(width * 0.12)
            logo_ratio = logo_width / logo.width
            logo_height = int(logo.height * logo_ratio)
            logo = logo.resize((logo_width, logo_height), Image.LANCZOS)

            padding = int(width * 0.03)
            logo_x = width - logo_width - padding
            logo_y = height - logo_height - padding
            base.paste(logo, (logo_x, logo_y), mask=logo)

            branded_path = Path("outputs") / "branded_image.png"
            base.save(str(branded_path), format="PNG")

            return f"BRANDED_IMAGE: {branded_path}"
        except Exception as e:
            return f"IMAGE_GENERATED (logo overlay failed: {e}): {generated_path}"

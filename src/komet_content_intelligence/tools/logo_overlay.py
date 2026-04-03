"""
Logo overlay tool — composites the Komet logo onto a generated image.
Uses Pillow to overlay a PNG logo with transparent background onto
the bottom-right corner of the generated image.
"""

import os
from pathlib import Path
from crewai.tools import BaseTool
from PIL import Image


def _find_logo() -> str:
    """Find the Komet logo PNG in config directory."""
    for base in [Path(__file__).parent.parent.parent.parent, Path.cwd()]:
        for name in ["komet_logo.png", "logo.png", "komet-logo.png"]:
            path = base / "config" / "brands" / name
            if path.exists():
                return str(path)
    return ""


class LogoOverlayTool(BaseTool):
    name: str = "Logo Overlay"
    description: str = """
    Add the Komet logo to a generated image. Input: path to the image file.
    Composites the Komet logo (PNG with transparent background) onto the
    bottom-right corner of the image. Returns path to the final branded image.
    """

    def _run(self, image_path: str) -> str:
        logo_path = _find_logo()

        if not logo_path:
            return (
                f"Logo overlay skipped — no logo file found. "
                f"Place komet_logo.png in config/brands/. "
                f"Original image at: {image_path}"
            )

        # Clean the image path (remove any "IMAGE_GENERATED: " prefix)
        clean_path = image_path.replace("IMAGE_GENERATED: ", "").strip()

        try:
            base = Image.open(clean_path).convert("RGBA")
            logo = Image.open(logo_path).convert("RGBA")

            width, height = base.size

            # Scale logo to ~12% of image width
            logo_width = int(width * 0.12)
            logo_ratio = logo_width / logo.width
            logo_height = int(logo.height * logo_ratio)
            logo = logo.resize((logo_width, logo_height), Image.LANCZOS)

            # Position: bottom-right with padding
            padding = int(width * 0.03)
            logo_x = width - logo_width - padding
            logo_y = height - logo_height - padding

            # Composite
            base.paste(logo, (logo_x, logo_y), mask=logo)

            # Save final image
            output_path = Path("outputs") / "branded_image.png"
            output_path.parent.mkdir(exist_ok=True)
            base.save(str(output_path), format="PNG")

            return f"BRANDED_IMAGE: {output_path}"

        except Exception as e:
            return f"Logo overlay error: {str(e)[:300]}. Original image at: {clean_path}"

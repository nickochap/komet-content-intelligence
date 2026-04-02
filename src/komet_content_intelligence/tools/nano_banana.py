import os
import requests
from crewai.tools import BaseTool


class NanoBananaTool(BaseTool):
    name: str = "Image Generator"
    description: str = "Generate a professional B2B LinkedIn image. Input: image description. Returns image URL."

    def _run(self, prompt: str, aspect_ratio: str = "4:5") -> str:
        api_key = os.getenv("NANO_BANANA_API_KEY")

        # Prepend Komet brand direction to every prompt
        brand_prompt = (
            "Professional B2B Salesforce consultancy visual. "
            "Dark navy background (#0B1A2B) with teal accent (#1D9E75). "
            "Clean, authoritative, not consumer lifestyle. "
            "No aspirational student imagery. "
            f"{prompt}"
        )

        response = requests.post(
            "https://nanobananaapi.ai/generate",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"prompt": brand_prompt, "aspect_ratio": aspect_ratio, "quality": "pro"}
        )
        result = response.json()
        return result.get("image_url", "Image generation failed — check API key and prompt")

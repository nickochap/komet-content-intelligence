import yaml
from pathlib import Path
from crewai.tools import BaseTool


def _load_proof_data() -> dict:
    """Load proof library from YAML config."""
    for base in [Path(__file__).parent.parent.parent.parent, Path.cwd()]:
        path = base / "config" / "proof_library.yaml"
        if path.exists():
            with open(path) as f:
                return yaml.safe_load(f)
    raise FileNotFoundError("config/proof_library.yaml not found")


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
        data = _load_proof_data()

        # Build lookup from both sections
        lookup = {}
        for section_key in ["micro_stories", "patterns"]:
            section = data.get(section_key, {})
            if section:
                lookup.update(section)

        requested_ids = [pid.strip() for pid in proof_ids.split(",")]
        results = []

        for pid in requested_ids:
            item = lookup.get(pid)
            if item:
                results.append(
                    f"ID: {pid}\n"
                    f"Type: {item.get('type', '')}\n"
                    f"Title: {item.get('title', '')}\n"
                    f"CLAIMABLE: {item.get('claimable', '').strip()}\n"
                    f"BACKGROUND ONLY: {item.get('background', '').strip()}\n"
                    f"Anonymisation: {item.get('anonymisation', '')}\n"
                    f"Tags: {', '.join(item.get('tags', []))}\n"
                    "---"
                )
            else:
                results.append(f"ID: {pid} — NOT FOUND in proof library\n---")

        return "\n".join(results)

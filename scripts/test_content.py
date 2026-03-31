"""
Full content crew end-to-end test.
Usage: uv run python scripts/test_content.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from crews.content.crew import ContentCrew
from dotenv import load_dotenv
load_dotenv()

# Standard test
STANDARD_TEST = """
Topic: Why most Salesforce implementations fail in education
Format: LinkedIn post
Audience: Education CEO / Head of Admissions at an Australian RTO or private college
Product anchor: Sales Cloud
"""

# Agentforce test (should trigger Caden review flag)
AGENTFORCE_TEST = """
Topic: How Agentforce can reduce admissions team workload
Format: LinkedIn post
Audience: Head of Admissions at an Australian private college
Product anchor: Agentforce
"""

LINKEDIN_REQUIRED_SECTIONS = [
    "## FINAL POST",
    "## ALTERNATE HOOK 1",
    "## ALTERNATE HOOK 2",
    "## ALTERNATE CTA",
    "## FOLLOW-UP COMMENT 1",
    "## FOLLOW-UP COMMENT 2",
    "## FOLLOW-UP COMMENT 3",
    "## IMAGE BRIEF",
    "## RATIONALE",
    "## PROOF USED",
]

BLOG_REQUIRED_SECTIONS = [
    "## ARTICLE",
    "## SEO TITLE",
    "## META DESCRIPTION",
    "## LINKEDIN DERIVATIVE POST",
    "## REPURPOSED SNIPPET 1",
    "## REPURPOSED SNIPPET 2",
    "## REPURPOSED SNIPPET 3",
    "## IMAGE BRIEF",
    "## PROOF USED",
]


def check_package_completeness(output: str, content_type: str = "linkedin") -> list:
    """Returns list of missing sections. Empty list = complete package."""
    required = LINKEDIN_REQUIRED_SECTIONS if content_type == "linkedin" else BLOG_REQUIRED_SECTIONS
    return [s for s in required if s not in output]


def run_test(brief: str, label: str, content_type: str = "linkedin"):
    print(f"\n{'='*60}")
    print(f"TEST: {label}")
    print('='*60)
    result = ContentCrew().crew().kickoff(inputs={"content_brief": brief})

    print("\nOUTPUT:")
    print(result.raw)

    # Package completeness — primary success criterion
    missing = check_package_completeness(result.raw, content_type)
    if missing:
        print(f"\n--- INCOMPLETE PACKAGE — missing sections:")
        for s in missing:
            print(f"   {s}")
    else:
        print(f"\n+++ COMPLETE PACKAGE — all {content_type} sections present")

    if "AGENTFORCE_CONTENT" in result.raw:
        print("*** AGENTFORCE_CONTENT flagged — Brand Guardian will check claims against Salesforce docs")

    Path("outputs").mkdir(exist_ok=True)
    output_path = f"outputs/test_{label.replace(' ', '_').lower()}.md"
    with open(output_path, "w") as f:
        f.write(result.raw)
    print(f"\nSaved to {output_path}")


if __name__ == "__main__":
    test_type = sys.argv[1] if len(sys.argv) > 1 else "standard"

    if test_type == "agentforce":
        run_test(AGENTFORCE_TEST, "Agentforce Test")
    else:
        run_test(STANDARD_TEST, "Standard Test")

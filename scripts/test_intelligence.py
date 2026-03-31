"""
Intelligence crew end-to-end test.
Usage: uv run python scripts/test_intelligence.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from crews.intelligence.crew import IntelligenceCrew
from dotenv import load_dotenv
load_dotenv()


def run_test():
    print("\n" + "="*60)
    print("TEST: Intelligence Crew — Weekly Idea Generation")
    print("="*60)

    result = IntelligenceCrew().crew().kickoff()

    print("\nOUTPUT:")
    print(result.raw)

    # Basic validation
    idea_count = result.raw.count("##")
    print(f"\nIdeas found (approximate): {idea_count}")

    if idea_count >= 8:
        print("+++ Target met — 8+ ideas generated")
    else:
        print(f"--- Below target — only {idea_count} ideas (expected 8-10)")

    Path("outputs").mkdir(exist_ok=True)
    with open("outputs/test_intelligence.md", "w") as f:
        f.write(result.raw)
    print("\nSaved to outputs/test_intelligence.md")


if __name__ == "__main__":
    run_test()

#!/usr/bin/env python
"""
Entry point for Komet Content Intelligence on CrewAI AMP.

Dispatches to the correct pipeline based on the 'action' input:
  - full_pipeline (default): Content → Creative → Publisher
  - intelligence: Weekly autonomous research + idea generation
"""
from komet_content_intelligence.dispatcher import run_pipeline, run_intelligence


def run():
    """Called by AMP on kickoff. Reads inputs from AMP payload."""
    import sys
    import json

    # AMP passes inputs as a JSON string or dict
    inputs = {}
    if len(sys.argv) > 1:
        try:
            inputs = json.loads(sys.argv[1])
        except (json.JSONDecodeError, IndexError):
            pass

    # Default: full content pipeline
    if not inputs.get("content_brief"):
        inputs["content_brief"] = (
            "Topic: Why most Salesforce implementations fail in education\n"
            "Format: LinkedIn post\n"
            "Audience: Education CEO / Head of Admissions at an Australian RTO or private college\n"
            "Product anchor: Sales Cloud"
        )

    action = inputs.get("action", "full_pipeline")

    if action == "intelligence":
        return run_intelligence(inputs)
    else:
        return run_pipeline(inputs)


def train():
    """Train the crew with example iterations."""
    from komet_content_intelligence.crew import KometContentIntelligenceCrew

    inputs = {
        "content_brief": (
            "Topic: Why most Salesforce implementations fail in education\n"
            "Format: LinkedIn post\n"
            "Audience: Education CEO / Head of Admissions\n"
            "Product anchor: Sales Cloud"
        )
    }
    try:
        KometContentIntelligenceCrew().crew().train(
            n_iterations=int(input("How many iterations? ")),
            filename="trained_agents_data.pkl",
            inputs=inputs,
        )
    except Exception as e:
        raise Exception(f"Training failed: {e}")

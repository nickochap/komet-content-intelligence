#!/usr/bin/env python
from src.komet_content_intelligence.crew import KometContentIntelligenceCrew


def run():
    """Run the crew."""
    inputs = {
        "content_brief": "Topic: Why most Salesforce implementations fail in education\n"
        "Format: LinkedIn post\n"
        "Audience: Education CEO / Head of Admissions at an Australian RTO or private college\n"
        "Product anchor: Sales Cloud"
    }
    KometContentIntelligenceCrew().crew().kickoff(inputs=inputs)


def train():
    """Train the crew."""
    inputs = {
        "content_brief": "Topic: Why most Salesforce implementations fail in education\n"
        "Format: LinkedIn post\n"
        "Audience: Education CEO / Head of Admissions\n"
        "Product anchor: Sales Cloud"
    }
    try:
        KometContentIntelligenceCrew().crew().train(
            n_iterations=int(input("How many iterations? ")),
            filename="trained_agents_data.pkl",
            inputs=inputs,
        )
    except Exception as e:
        raise Exception(f"Training failed: {e}")

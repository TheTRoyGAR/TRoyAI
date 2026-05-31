import os
from crewai import LLM

OPUS = "claude-opus-4-8"
SONNET = "claude-sonnet-4-6"
HAIKU = "claude-haiku-4-5-20251001"


def get_llm(tier: str = "sonnet") -> LLM:
    model = {"opus": OPUS, "sonnet": SONNET, "haiku": HAIKU}.get(tier, SONNET)
    return LLM(
        model=model,
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        temperature=0.7,
    )

import os
from crewai import LLM

OPUS = "claude-opus-4-8"
SONNET = "claude-sonnet-4-6"
HAIKU = "claude-haiku-4-5-20251001"


def get_llm(tier: str = "sonnet") -> LLM:
    model = {"opus": OPUS, "sonnet": SONNET, "haiku": HAIKU}.get(tier, SONNET)
    # No `temperature` kwarg: the installed anthropic SDK's Messages.create()
    # no longer accepts it, and crewai passes through whatever LLM() is given
    # here verbatim, so setting it makes every single call fail with
    # "unexpected keyword argument 'temperature'" — found by actually running
    # a real LLM call, not assumed.
    # Without an explicit max_tokens, this defaults to 4096 — long tool calls
    # (e.g. a full report written as one FileWriterTool `content` argument)
    # get truncated mid-generation into malformed JSON, which CrewAI then
    # retries forever instead of failing, burning real API spend on every
    # retry without ever completing.
    return LLM(
        model=model,
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        max_tokens=8192,
    )

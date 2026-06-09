"""OpenAI vision analysis with structured outputs.

Uses the Responses API with a Pydantic schema so the model returns typed,
validated JSON instead of free text that needs regex parsing.
"""

import logging
import os

from openai import AsyncOpenAI

from schemas import SwingAnalysis

logger = logging.getLogger(__name__)

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")

SYSTEM_PROMPT = """\
You are an experienced golf coach analyzing sequential frames from a video of a
golf swing. The frames are provided in chronological order. For each frame,
identify the swing phase and assess posture, club position, swing plane, and
weight transfer. Then summarize the golfer's strengths, give prioritized
recommendations, and suggest practice drills. Be specific and encouraging, and
ground every observation in what is actually visible in the frames.
"""

_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI()
    return _client


async def analyze_swing(frames_b64: list[str]) -> SwingAnalysis:
    """Send base64-encoded JPEG frames to the model and get a structured analysis."""
    logger.info("Analyzing swing with %s (%d frames)", OPENAI_MODEL, len(frames_b64))

    user_content = [
        {
            "type": "input_text",
            "text": f"Here are {len(frames_b64)} chronological frames from my golf swing. Please analyze it.",
        },
        *(
            {"type": "input_image", "image_url": f"data:image/jpeg;base64,{frame}", "detail": "high"}
            for frame in frames_b64
        ),
    ]

    response = await get_client().responses.parse(
        model=OPENAI_MODEL,
        instructions=SYSTEM_PROMPT,
        input=[{"role": "user", "content": user_content}],
        text_format=SwingAnalysis,
    )

    analysis = response.output_parsed
    if analysis is None:
        raise RuntimeError("Model returned no parsed output")
    return analysis

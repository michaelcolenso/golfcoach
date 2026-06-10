"""Pydantic models shared by the API and the structured LLM output."""

from enum import Enum

from pydantic import BaseModel, Field


class SwingPhase(str, Enum):
    setup = "setup"
    takeaway = "takeaway"
    backswing = "backswing"
    top_of_swing = "top_of_swing"
    downswing = "downswing"
    impact = "impact"
    follow_through = "follow_through"


class FrameAnalysis(BaseModel):
    frame_index: int = Field(description="Zero-based index of the frame being analyzed")
    phase: SwingPhase = Field(description="The swing phase shown in this frame")
    observation: str = Field(description="What the golfer is doing in this frame: posture, club position, weight distribution")
    tip: str = Field(description="One specific, actionable coaching tip for this moment of the swing")


class SwingAnalysis(BaseModel):
    frames: list[FrameAnalysis] = Field(description="Per-frame analysis, one entry per provided image, in order")
    strengths: list[str] = Field(description="2-4 things the golfer is doing well")
    recommendations: list[str] = Field(description="3-5 prioritized, actionable improvements, most impactful first")
    drills: list[str] = Field(description="1-3 practice drills targeting the biggest issues")
    overall_feedback: str = Field(description="A short encouraging summary of the swing as a whole")


class AnalyzeResponse(BaseModel):
    filename: str
    frame_count: int
    selected_frames: list[str]
    feedback: SwingAnalysis

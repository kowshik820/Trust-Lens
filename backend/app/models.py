from typing import Any, Dict, List, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

RiskLevel = Literal["LOW", "MEDIUM", "HIGH"]
SignalSeverity = Literal["LOW", "MEDIUM", "HIGH"]


class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(..., min_length=1, max_length=10000, description="User provided content to assess.")

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Input text cannot be empty.")
        return cleaned


class Signal(BaseModel):
    type: str
    severity: SignalSeverity
    explanation: str


class AnalysisResponse(BaseModel):
    risk_level: RiskLevel
    risk_score: int
    status: str
    action: str
    summary: str
    signals: List[Signal]
    recommendations: List[str]
    rule_analysis: Dict[str, Any]
    analysis_id: str

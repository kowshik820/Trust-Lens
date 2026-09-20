import json
import os
import re
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.config import AWS_REGION, BEDROCK_MODEL_ID

SYSTEM_PROMPT = """
You are TrustLens, an AI-assisted digital trust and scam analysis system.

Analyze user-provided digital content for potential scam, phishing, impersonation, manipulation, financial fraud, recruitment fraud, and credential theft indicators.
Important rules:
- Do not make absolute claims.
- Do not invent external facts.
- Distinguish between observed evidence, inferred risk, and uncertainty.
- Use cautious language such as 'potential scam indicators' and 'AI-assisted risk assessment'.
- Never claim certainty that content is fraudulent.
- Return only strict JSON with the exact structure described below.

Required JSON schema:
{
  "risk_level": "LOW | MEDIUM | HIGH",
  "risk_score": 0,
  "summary": "...",
  "signals": [
    {
      "type": "...",
      "severity": "LOW | MEDIUM | HIGH",
      "explanation": "..."
    }
  ],
  "recommendations": ["..."]
}
"""


def is_bedrock_configured() -> bool:
    return bool(AWS_REGION and BEDROCK_MODEL_ID)


def _strip_code_fences(text: str) -> str:
    cleaned = text.strip()
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, flags=re.DOTALL | re.IGNORECASE)
    if match:
        cleaned = match.group(1).strip()
    return cleaned


def _normalize_signal(signal: Dict[str, Any]) -> Dict[str, str]:
    signal_type = str(signal.get("type", "General risk")).strip()
    severity = str(signal.get("severity", "MEDIUM")).strip().upper()
    if severity not in {"LOW", "MEDIUM", "HIGH"}:
        severity = "MEDIUM"
    explanation = str(signal.get("explanation", "This signal was identified by the model.")).strip()
    return {"type": signal_type, "severity": severity, "explanation": explanation}


def _normalize_result(payload: Dict[str, Any]) -> Dict[str, Any]:
    risk_level = str(payload.get("risk_level", "LOW")).strip().upper()
    if risk_level not in {"LOW", "MEDIUM", "HIGH"}:
        risk_level = "LOW"

    risk_score = int(payload.get("risk_score", 0))
    risk_score = max(0, min(100, risk_score))

    summary = str(payload.get("summary", "AI-assisted assessment completed."))
    recommendations = payload.get("recommendations", [])
    if not isinstance(recommendations, list):
        recommendations = []
    recommendations = [str(item).strip() for item in recommendations if str(item).strip()]

    signals = payload.get("signals", [])
    if not isinstance(signals, list):
        signals = []
    signals = [_normalize_signal(item) for item in signals if isinstance(item, dict)]

    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "summary": summary,
        "signals": signals,
        "recommendations": recommendations,
    }


def parse_bedrock_json(raw_text: str) -> Dict[str, Any]:
    cleaned = _strip_code_fences(raw_text)
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed JSON returned by Amazon Bedrock: {exc}") from exc

    if not isinstance(parsed, dict):
        raise ValueError("Bedrock response is not a JSON object.")

    return _normalize_result(parsed)


def analyze_with_bedrock(text: str) -> Optional[Dict[str, Any]]:
    if not is_bedrock_configured():
        return None

    try:
        client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
        prompt = (
            "Analyze the following content for potential scam, phishing, impersonation, credential theft, "
            "financial deception, or manipulation indicators. Return only strict JSON.\n\n"
            f"Content:\n{text}"
        )
        response = client.converse(
            modelId=BEDROCK_MODEL_ID,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            system=[{"text": SYSTEM_PROMPT}],
            inferenceConfig={"temperature": 0.1, "maxTokens": 800},
        )

        content_blocks = response.get("output", {}).get("message", {}).get("content", [])
        if not content_blocks:
            raise ValueError("Amazon Bedrock returned no content.")

        raw_text = content_blocks[0].get("text", "")
        return parse_bedrock_json(raw_text)
    except (ClientError, BotoCoreError, ValueError) as exc:
        raise RuntimeError(f"Bedrock analysis failed: {str(exc)}") from exc
    except Exception as exc:  # pragma: no cover - defensive fallback
        raise RuntimeError("Bedrock analysis failed due to an unexpected error.") from exc

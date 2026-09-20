"""Risk analysis orchestration used by FastAPI and AWS Lambda.

Cloud integrations are deliberately optional so local development keeps working.
"""

import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.analyzer import analyze_text
from app.bedrock import analyze_with_bedrock, is_bedrock_configured
from app.scoring import build_risk_summary, calculate_risk_score, classify_risk, determine_risk_level
from app.threat_lookup import lookup_threats
from app.url_analyzer import analyze_urls_in_text

logger = logging.getLogger(__name__)


def _tool_findings(text: str) -> Dict[str, Any]:
    lowered = text.lower()
    urls = analyze_urls_in_text(text)
    return {
        "url_analysis": urls,
        "threat_lookup": lookup_threats(text),
        "email_analysis": {
            "has_email": "@" in text,
            "signals": analyze_text(text),
        },
        "job_scam_analysis": {
            "is_job_related": any(term in lowered for term in ("job", "hiring", "recruiter", "interview", "internship")),
            "signals": analyze_text(text),
        },
    }


def _merge_signals(rule_signals: List[Dict[str, str]], ai_signals: Any) -> List[Dict[str, str]]:
    merged = list(rule_signals)
    if not isinstance(ai_signals, list):
        return merged
    for item in ai_signals:
        if not isinstance(item, dict):
            continue
        signal = {
            "type": str(item.get("type", "General risk")),
            "severity": str(item.get("severity", "MEDIUM")).upper(),
            "explanation": str(item.get("explanation", "AI-assisted risk signal.")),
        }
        if signal["severity"] not in {"LOW", "MEDIUM", "HIGH"}:
            signal["severity"] = "MEDIUM"
        if not any(existing["type"] == signal["type"] for existing in merged):
            merged.append(signal)
    return merged


def _apply_cedar_policy(risk_score: int) -> Dict[str, Any]:
    """Evaluate the same safety contract represented in aws/policies/trustlens.cedar.

    The pure-Python decision keeps Lambda dependency-light. The Cedar policy file is
    the canonical policy artifact for teams that enforce it in their deployment pipeline.
    """
    policy = classify_risk(risk_score)
    return {
        "decision": "DENY" if policy["action"] == "BLOCK" else "ALLOW",
        "action": policy["action"],
        "status": policy["status"],
    }


def analyze_with_agent(text: str) -> Dict[str, Any]:
    rule_signals = analyze_text(text)
    tools = _tool_findings(text)
    ai_result = None

    if is_bedrock_configured():
        try:
            ai_result = analyze_with_bedrock(text)
        except RuntimeError as exc:
            logger.warning("Bedrock unavailable; continuing with deterministic tools: %s", exc)

    signals = _merge_signals(rule_signals, ai_result.get("signals") if ai_result else None)
    score = calculate_risk_score(signals)
    policy = _apply_cedar_policy(score)
    recommendations = ai_result.get("recommendations", []) if ai_result else []
    if not recommendations:
        recommendations = [
            "Do not click links or open attachments until the sender is independently verified.",
            "Do not share OTPs, PINs, passwords, or recovery codes.",
            "Verify the organization using contact details from its official website.",
        ]
    return {
        "risk_level": determine_risk_level(score),
        "risk_score": score,
        "status": policy["status"],
        "action": policy["action"],
        "policy_decision": policy["decision"],
        "summary": (ai_result or {}).get("summary") or build_risk_summary(signals, score),
        "signals": signals,
        "recommendations": [str(item) for item in recommendations if item],
        "rule_analysis": {
            "tool_findings": tools,
            "signal_count": len(signals),
            "bedrock_used": bool(ai_result),
            "policy": policy,
        },
        "analysis_id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def persist_analysis(result: Dict[str, Any]) -> None:
    table_name = os.getenv("ANALYSIS_TABLE_NAME", "")
    if not table_name:
        return
    try:
        import boto3

        boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1")).Table(table_name).put_item(Item={
            "analysis_id": result["analysis_id"],
            "created_at": result["created_at"],
            "risk_level": result["risk_level"],
            "risk_score": result["risk_score"],
            "status": result["status"],
            "summary": result["summary"],
        })
    except Exception as exc:  # Cloud persistence must not break safety analysis.
        logger.warning("DynamoDB persistence unavailable: %s", exc)

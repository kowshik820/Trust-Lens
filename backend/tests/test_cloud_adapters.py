import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import agent
from lambda_handler import handler


def test_agent_composes_tools_without_bedrock(monkeypatch):
    monkeypatch.setattr(agent, "is_bedrock_configured", lambda: False)
    result = agent.analyze_with_agent("Urgent: pay a training fee for this job offer.")

    assert result["risk_score"] > 0
    assert result["policy_decision"] in {"ALLOW", "DENY"}
    assert "job_scam_analysis" in result["rule_analysis"]["tool_findings"]
    assert result["rule_analysis"]["bedrock_used"] is False


def test_lambda_rejects_empty_input():
    response = handler({"body": json.dumps({"text": ""})}, None)

    assert response["statusCode"] == 400
    assert "cannot be empty" in json.loads(response["body"])["detail"]


def test_lambda_returns_analysis_without_cloud_services(monkeypatch):
    monkeypatch.setattr(agent, "is_bedrock_configured", lambda: False)
    response = handler({"body": json.dumps({"text": "Please send your OTP immediately."})}, None)

    assert response["statusCode"] == 200
    assert json.loads(response["body"])["risk_level"] in {"LOW", "MEDIUM", "HIGH"}

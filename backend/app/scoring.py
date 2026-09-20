from typing import Any, Dict, List

RISK_POLICY = {
    "LOW": {"min": 0, "max": 30, "risk_level": "LOW", "status": "Low Risk", "action": "ALLOW_WITH_NOTICE", "message": "Low detected risk — always verify the source before proceeding."},
    "MEDIUM": {"min": 31, "max": 70, "risk_level": "MEDIUM", "status": "Caution", "action": "REQUIRE_CONFIRMATION", "message": "Caution — potential risk detected. Review the source before proceeding."},
    "HIGH": {"min": 71, "max": 100, "risk_level": "HIGH", "status": "High Risk", "action": "BLOCK", "message": "High Risk — suspicious content detected. Do not open or interact until independently verified."},
}


def calculate_risk_score(signals: List[Dict[str, str]]) -> int:
    if not signals:
        return 8

    weights = {
        "LOW": 5,
        "MEDIUM": 12,
        "HIGH": 22,
    }

    score = sum(weights.get(signal.get("severity", "LOW"), 5) for signal in signals)
    return min(100, score)


def classify_risk(score: int) -> Dict[str, Any]:
    score_value = max(0, min(100, int(score)))
    for policy in RISK_POLICY.values():
        if policy["min"] <= score_value <= policy["max"]:
            return {
                "risk_level": policy["risk_level"],
                "status": policy["status"],
                "action": policy["action"],
                "message": policy["message"],
                "threshold_min": policy["min"],
                "threshold_max": policy["max"],
            }
    return {
        "risk_level": "LOW",
        "status": "Low Risk",
        "action": "ALLOW_WITH_NOTICE",
        "message": "Low detected risk — always verify the source before proceeding.",
        "threshold_min": 0,
        "threshold_max": 30,
    }


def determine_risk_level(score: int) -> str:
    return classify_risk(score)["risk_level"]


def build_risk_summary(signals: List[Dict[str, str]], score: int) -> str:
    if not signals:
        return "No clear scam indicators were detected in the supplied content. Independent verification is still recommended before acting."

    risk_level = determine_risk_level(score)
    return (
        f"AI-assisted risk assessment indicates {risk_level.lower()} risk. "
        "Several patterns suggest manipulation, impersonation, or financial pressure."
    )

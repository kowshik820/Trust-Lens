import logging
import re
import uuid
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.analyzer import analyze_text
from app.bedrock import analyze_with_bedrock, is_bedrock_configured
from app.config import ALLOWED_ORIGINS, MAX_INPUT_LENGTH
from app.models import AnalysisResponse, AnalyzeRequest, Signal
from app.scoring import build_risk_summary, calculate_risk_score, classify_risk, determine_risk_level
from app.url_analyzer import analyze_urls_in_text

logger = logging.getLogger(__name__)

app = FastAPI(
    title="TrustLens",
    version="0.1.0",
    description="AI-assisted digital trust and scam analysis API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _normalize_risk(score: int) -> str:
    if score >= 70:
        return "HIGH"
    if score >= 35:
        return "MEDIUM"
    return "LOW"


def _detect_signals(text: str) -> List[Signal]:
    lowered = text.lower()
    signals: List[Signal] = []
    normalized = {
        "urgency": ["immediately", "today", "within 30 minutes", "urgent", "asap", "act now"],
        "suspension": ["account suspended", "security alert", "verify your account", "restricted access"],
        "otp": ["otp", "one-time password", "verification code"],
        "password": ["password", "reset your password", "your password will expire"],
        "pin": ["pin", "personal identification number"],
        "payment": ["payment required", "send money", "wire transfer", "bank transfer", "pay now", "processing fee"],
        "registration_fee": ["registration fee", "activation fee", "membership fee"],
        "lottery": ["lottery", "winner", "prize claim", "congratulations you won"],
        "investment": ["guaranteed returns", "double your money", "investment opportunity", "quick profit"],
        "job_payment": ["pay for training", "internship fee", "job application fee", "security deposit"],
        "credential": ["enter your credentials", "provide your login", "email and password", "username and password"],
        "identification": ["id card", "national id", "passport", "driver license", "ssn", "aadhaar"],
        "impersonation": ["from hr", "from bank", "official support", "from management"],
    }

    for signal_type, phrases in normalized.items():
        for phrase in phrases:
            if phrase in lowered:
                signal_map = {
                    "urgency": ("Urgency", "HIGH", "The message creates a short deadline to pressure a rapid response."),
                    "suspension": ("Account suspension claim", "HIGH", "The message tries to trigger alarm by claiming the account or access is at risk."),
                    "otp": ("OTP request", "HIGH", "The message requests a temporary verification code that should not be shared."),
                    "password": ("Password request", "HIGH", "The message asks for a secret login credential or password."),
                    "pin": ("PIN request", "HIGH", "The message requests a numeric personal access code that should remain private."),
                    "payment": ("Payment request", "HIGH", "The message asks for funds or a payment before action is independently verified."),
                    "registration_fee": ("Registration fee request", "MEDIUM", "The message requests a fee to participate or proceed."),
                    "lottery": ("Prize or lottery claim", "MEDIUM", "The message presents a prize or winning claim without clear independent verification."),
                    "investment": ("Investment scam pattern", "HIGH", "The message promises unusually high or guaranteed financial returns."),
                    "job_payment": ("Job or recruitment payment request", "HIGH", "The message asks the recipient to pay for a job, training, or onboarding step."),
                    "credential": ("Credential harvesting", "HIGH", "The message tries to collect login details or account information."),
                    "identification": ("Sensitive identification request", "HIGH", "The message requests personal identification details that are unnecessary for ordinary verification."),
                    "impersonation": ("Impersonation pattern", "MEDIUM", "The message uses authority or organization language that may be intended to imitate a trusted sender."),
                }
                label, severity, explanation = signal_map[signal_type]
                if not any(existing.type == label for existing in signals):
                    signals.append(Signal(type=label, severity=severity, explanation=explanation))
                break

    if re.search(r"https?://", text):
        url_signals = [
            "http://",
            "bit.ly",
            "tinyurl",
            "t.co",
            "go.redirect",
            "verify-now",
            "secure-login",
        ]
        for phrase in url_signals:
            if phrase in lowered:
                if not any(existing.type == "Suspicious URL" for existing in signals):
                    signals.append(
                        Signal(
                            type="Suspicious URL",
                            severity="MEDIUM",
                            explanation="The message includes a URL pattern that is commonly used in phishing or scam attempts.",
                        )
                    )
                break

    return signals


def _build_recommendations(signals: List[Signal]) -> List[str]:
    recs = [
        "Do not click links or open attachments from suspicious messages until the sender is independently verified.",
        "Do not share OTPs, PINs, passwords, or account recovery codes with anyone.",
        "Verify the organization using official contact information found on its legitimate website, not the message itself.",
    ]

    if any(signal.type in {"Payment request", "Registration fee request", "Job or recruitment payment request"} for signal in signals):
        recs.append("If money has already been sent, contact the relevant financial institution promptly and report the payment concern.")

    if any(signal.type in {"Credential harvesting", "Sensitive identification request"} for signal in signals):
        recs.append("Treat any request for account credentials or personal ID details as high-risk until verified independently.")

    return recs


def _build_rule_analysis(text: str, signals: List[Signal]) -> Dict[str, Any]:
    urls = re.findall(r"https?://\S+", text)
    return {
        "url_count": len(urls),
        "url_examples": urls[:5],
        "signal_count": len(signals),
        "contains_urgency": any("Urgency" == signal.type for signal in signals),
        "contains_payment_request": any("Payment request" == signal.type for signal in signals),
        "contains_credential_request": any("Credential harvesting" == signal.type for signal in signals),
        "contains_impersonation_pattern": any("Impersonation pattern" == signal.type for signal in signals),
    }


@app.get("/")
def read_root() -> Dict[str, str]:
    return {
        "name": "TrustLens",
        "status": "online",
        "message": "Digital Trust & Scam Analyzer API",
    }


@app.get("/health")
def health_check() -> Dict[str, str]:
    return {
        "status": "ok",
        "service": "TrustLens API",
    }


@app.post("/analyze", response_model=AnalysisResponse)
def analyze_content(payload: AnalyzeRequest) -> AnalysisResponse:
    text = payload.text.strip()

    if not text:
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")

    if len(text) > MAX_INPUT_LENGTH:
        raise HTTPException(
            status_code=413,
            detail=f"Input text exceeds the maximum supported size of {MAX_INPUT_LENGTH} characters.",
        )

    try:
        signals = _detect_signals(text)
        if not signals:
            signals = analyze_text(text)

        url_findings = analyze_urls_in_text(text)
        if url_findings:
            for item in url_findings:
                if item.get("suspicious_signals"):
                    existing = any(signal.type == "Suspicious URL" for signal in signals)
                    if not existing:
                        signals.append(
                            Signal(
                                type="Suspicious URL",
                                severity="MEDIUM",
                                explanation=item.get("summary", "Suspicious URL characteristics detected."),
                            )
                        )

        recommendations = _build_recommendations(signals)
        ai_result = None
        if is_bedrock_configured():
            try:
                ai_result = analyze_with_bedrock(text)
            except RuntimeError as exc:
                logger.warning("Bedrock analysis unavailable: %s", exc)
                ai_result = None

        if ai_result:
            ai_signals = ai_result.get("signals", [])
            if isinstance(ai_signals, list):
                for item in ai_signals:
                    if isinstance(item, dict):
                        signal_exists = any(
                            existing.type == item.get("type", "General risk") and existing.severity == item.get("severity", "MEDIUM")
                            for existing in signals
                        )
                        if not signal_exists:
                            signals.append(
                                Signal(
                                    type=str(item.get("type", "General risk")),
                                    severity=str(item.get("severity", "MEDIUM")).upper(),
                                    explanation=str(item.get("explanation", "AI-assisted risk signal.")),
                                )
                            )

            if ai_result.get("recommendations"):
                recommendations = [str(item) for item in ai_result["recommendations"] if item]

            risk_score = calculate_risk_score([signal.model_dump() for signal in signals])
            risk_level = determine_risk_level(risk_score)
            risk_policy = classify_risk(risk_score)
            summary = ai_result.get("summary") or build_risk_summary([signal.model_dump() for signal in signals], risk_score)
        else:
            risk_score = calculate_risk_score([signal.model_dump() for signal in signals])
            risk_level = determine_risk_level(risk_score)
            risk_policy = classify_risk(risk_score)
            summary = build_risk_summary([signal.model_dump() for signal in signals], risk_score)

        if not signals:
            summary = "No high-confidence scam indicators were detected in the provided content. Use caution and verify independently before acting."
            risk_policy = classify_risk(risk_score)

        return AnalysisResponse(
            risk_level=risk_level,
            risk_score=risk_score,
            status=risk_policy["status"],
            action=risk_policy["action"],
            summary=summary,
            signals=signals,
            recommendations=recommendations,
            rule_analysis=_build_rule_analysis(text, signals),
            analysis_id=str(uuid.uuid4()),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive fallback
        raise HTTPException(status_code=500, detail="An unexpected server error occurred while analyzing the content.") from exc


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def generic_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected server error occurred. Please try again later."},
    )

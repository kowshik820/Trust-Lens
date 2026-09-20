import re
from typing import Dict, List, Tuple


class Signal:
    def __init__(self, type: str, severity: str, explanation: str):
        self.type = type
        self.severity = severity
        self.explanation = explanation

    def to_dict(self) -> Dict[str, str]:
        return {
            "type": self.type,
            "severity": self.severity,
            "explanation": self.explanation,
        }


class ScamAnalyzer:
    def __init__(self):
        self.patterns = {
            "urgency": {
                "keywords": [
                    "urgent",
                    "immediately",
                    "today",
                    "asap",
                    "act now",
                    "within 30 minutes",
                    "time is running out",
                    "do not delay",
                    "before midnight",
                    "action required",
                    "reply now",
                ],
                "severity": "HIGH",
                "explanation": "The message creates a short deadline to pressure the recipient into acting quickly.",
            },
            "payment_request": {
                "keywords": [
                    "pay now",
                    "send money",
                    "wire transfer",
                    "bank transfer",
                    "processing fee",
                    "registration fee",
                    "activation fee",
                    "transaction fee",
                    "payment required",
                    "pay a",
                    "pay the",
                    "onboarding fee",
                    "training fee",
                    "security deposit",
                    "admin fee",
                    "deposit",
                    "advance payment",
                ],
                "severity": "HIGH",
                "explanation": "The message asks for money or a fee before the request is independently verified.",
            },
            "otp_request": {
                "keywords": [
                    "otp",
                    "one-time password",
                    "verification code",
                    "code sent to your phone",
                ],
                "severity": "HIGH",
                "explanation": "The message requests a temporary verification code that should not be shared with anyone.",
            },
            "password_request": {
                "keywords": [
                    "password",
                    "your password",
                    "login password",
                    "account password",
                    "enter your password",
                    "login credentials",
                ],
                "severity": "HIGH",
                "explanation": "The message requests a login secret that should remain private.",
            },
            "pin_request": {
                "keywords": [
                    "pin",
                    "personal identification number",
                    "card pin",
                ],
                "severity": "HIGH",
                "explanation": "The message requests a personal identification number that should never be shared.",
            },
            "personal_information_request": {
                "keywords": [
                    "national id",
                    "passport",
                    "driver license",
                    "ssn",
                    "aadhaar",
                    "government id",
                    "id card",
                    "full address",
                    "date of birth",
                    "banking details",
                    "bank details",
                    "routing number",
                    "account details",
                    "cvv",
                    "identity document",
                ],
                "severity": "HIGH",
                "explanation": "The message asks for personal identification or private details that are often used in fraud or impersonation.",
            },
            "fake_job_request": {
                "keywords": [
                    "job offer",
                    "internship",
                    "remote role",
                    "recruiter",
                    "hiring immediately",
                    "pay for training",
                    "application fee",
                    "interview fee",
                    "security deposit",
                    "selected you for the role",
                    "selected you for an interview",
                    "employment approved",
                    "onboarding fee",
                    "first day payment",
                    "we are hiring",
                    "hired immediately",
                ],
                "severity": "HIGH",
                "explanation": "The message uses job or recruitment language while also asking for money or an unusual upfront step.",
            },
            "investment_scam": {
                "keywords": [
                    "guaranteed return",
                    "double your money",
                    "quick profit",
                    "investment opportunity",
                    "crypto investment",
                    "passive income",
                    "high return",
                    "guaranteed income",
                    "zero risk",
                    "quick cash",
                    "safe investment",
                ],
                "severity": "HIGH",
                "explanation": "The message promises unusually strong or guaranteed financial returns without a realistic basis.",
            },
            "verification_language": {
                "keywords": [
                    "verify your account",
                    "confirm your identity",
                    "secure your account",
                    "account verification",
                    "official notice",
                    "security alert",
                    "suspended account",
                    "verify now",
                    "confirm via the secure login link",
                    "secure login",
                    "account has been suspended",
                ],
                "severity": "MEDIUM",
                "explanation": "The message uses security or verification language to create urgency and trust before a request is evaluated.",
            },
            "impersonation": {
                "keywords": [
                    "from hr",
                    "from bank",
                    "official support",
                    "from management",
                    "from your bank",
                    "our team",
                    "customer service",
                    "finance team",
                    "hr@",
                    "this is kate from hr",
                    "this is andreas from the finance team",
                ],
                "severity": "MEDIUM",
                "explanation": "The message uses authority or institutional language that may be intended to imitate a trusted sender.",
            },
        }

    def analyze(self, text: str) -> List[Dict[str, str]]:
        cleaned = (text or "").strip()
        if not cleaned:
            return []

        lower = cleaned.lower()
        signals: List[Dict[str, str]] = []
        seen = set()

        for rule_name, item in self.patterns.items():
            matches = [keyword for keyword in item["keywords"] if keyword in lower]
            if matches:
                signal_type = self._humanize(rule_name)
                if signal_type not in seen:
                    signals.append(
                        {
                            "type": signal_type,
                            "severity": item["severity"],
                            "explanation": item["explanation"],
                        }
                    )
                    seen.add(signal_type)

        url_risk = self._detect_url_risk(lower)
        if url_risk and "URL risk indicator" not in seen:
            signals.append(
                {
                    "type": "URL risk indicator",
                    "severity": "MEDIUM",
                    "explanation": url_risk,
                }
            )
            seen.add("URL risk indicator")

        if self._has_multiple_high_risk_indicators(lower):
            if not any(signal["type"] == "Urgency" for signal in signals):
                signals.append(
                    {
                        "type": "Urgency",
                        "severity": "HIGH",
                        "explanation": "The message combines several pressure cues that increase the likelihood of manipulation.",
                    }
                )

        return signals

    def _detect_url_risk(self, text: str) -> str:
        url_matches = re.findall(r"https?://[^\s]+", text)
        if not url_matches:
            return ""

        suspicious_domain_terms = [
            "verify",
            "secure",
            "login",
            "account",
            "bank",
            "payment",
            "invoice",
            "confirm",
            "update",
            "action",
        ]
        for url in url_matches:
            domain = url.split("//", 1)[-1].split("/", 1)[0].lower()
            if any(term in domain for term in suspicious_domain_terms):
                return "The content includes a URL with verification or login-oriented language commonly used in phishing attempts."

        return "The content contains a link that should be validated independently before clicking."

    def _has_multiple_high_risk_indicators(self, text: str) -> bool:
        critical_rules = [
            "urgent",
            "password",
            "otp",
            "verification code",
            "send money",
            "payment",
            "wire transfer",
            "guaranteed return",
            "passport",
            "ssn",
            "pin",
        ]
        matches = sum(1 for phrase in critical_rules if phrase in text)
        return matches >= 2

    def _humanize(self, rule_name: str) -> str:
        names = {
            "urgency": "Urgency",
            "payment_request": "Payment request",
            "otp_request": "OTP request",
            "password_request": "Password request",
            "pin_request": "PIN request",
            "personal_information_request": "Personal information request",
            "fake_job_request": "Recruitment scam pattern",
            "investment_scam": "Investment scam indicator",
            "verification_language": "Suspicious verification language",
            "impersonation": "Impersonation indicator",
        }
        return names.get(rule_name, rule_name.replace("_", " ").title())


DEFAULT_ANALYZER = ScamAnalyzer()


def analyze_text(text: str) -> List[Dict[str, str]]:
    return DEFAULT_ANALYZER.analyze(text)

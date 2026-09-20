import re
from typing import Dict, List
from urllib.parse import urlparse


def extract_urls(text: str) -> List[str]:
    return re.findall(r'https?://[^\s)>"\']+', text or "")


def analyze_url(url: str) -> Dict[str, object]:
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    suspicious = []

    if parsed.hostname and parsed.hostname.replace(".", "").isdigit():
        suspicious.append("IP-address URL detected.")

    if parsed.scheme.lower() != "https":
        suspicious.append("HTTP is used instead of HTTPS.")

    if domain.startswith("www."):
        domain = domain[4:]

    if domain.count(".") >= 3:
        suspicious.append("Excessive subdomains detected.")

    shorteners = ["bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "tiny.cc"]
    if any(shortener in domain for shortener in shorteners):
        suspicious.append("URL shortening service detected.")

    misleading_keywords = ["verify", "secure", "login", "account", "bank", "invoice", "payment"]
    if any(keyword in domain for keyword in misleading_keywords):
        suspicious.append("Misleading keywords detected in the URL structure.")

    if "@" in url or "//" in url:
        suspicious.append("Suspicious URL characters detected.")

    findings = {
        "url": url,
        "domain": domain,
        "is_ip_address": bool(parsed.hostname and parsed.hostname.replace(".", "").isdigit()),
        "uses_https": parsed.scheme.lower() == "https",
        "has_shortener": any(shortener in domain for shortener in shorteners),
        "suspicious_signals": suspicious,
        "summary": "Suspicious URL characteristics detected." if suspicious else "No obvious suspicious URL characteristics were detected.",
    }
    return findings


def analyze_urls_in_text(text: str) -> List[Dict[str, object]]:
    urls = extract_urls(text)
    return [analyze_url(url) for url in urls]

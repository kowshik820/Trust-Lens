import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.analyzer import analyze_text
from app.main import app


def test_empty_input_returns_no_signals():
    assert analyze_text("   ") == []


def test_urgency_detection():
    result = analyze_text("URGENT! Verify now before midnight or your account will be locked.")
    assert any(signal["type"] == "Urgency" for signal in result)


def test_payment_detection():
    result = analyze_text("Pay now via bank transfer to receive your refund.")
    assert any(signal["type"] == "Payment request" for signal in result)


def test_credential_request_detection():
    result = analyze_text("Please enter your password and OTP to proceed.")
    assert any(signal["type"] == "Password request" for signal in result)
    assert any(signal["type"] == "OTP request" for signal in result)


def test_url_extraction():
    from app.url_analyzer import extract_urls

    text = "Click https://bit.ly/abc and https://example.com to continue."
    urls = extract_urls(text)
    assert len(urls) == 2
    assert "https://bit.ly/abc" in urls


def test_safe_message():
    result = analyze_text("Hello, I am following up on our meeting tomorrow at 3 PM.")
    assert result == []


def test_high_risk_message():
    result = analyze_text("URGENT! Your bank account is suspended. Verify your identity now, send your OTP, and pay the processing fee immediately.")
    assert any(signal["type"] == "Urgency" for signal in result)
    assert any(signal["type"] == "OTP request" for signal in result)
    assert any(signal["type"] == "Payment request" for signal in result)


def test_email_job_offer_with_fee_and_identity_request():
    result = analyze_text(
        "From: HR@company.com\nSubject: Hiring update\nHello, your application is approved. Please pay a $120 onboarding fee and send your passport and banking details before your first day."
    )
    assert any(signal["type"] == "Recruitment scam pattern" for signal in result)
    assert any(signal["type"] == "Payment request" for signal in result)
    assert any(signal["type"] == "Personal information request" for signal in result)


def test_url_verification_link_detection():
    result = analyze_text("Access the secure login link here: https://secure-login-account-check.com/verify")
    assert any(signal["type"] in {"Suspicious verification language", "URL risk indicator"} for signal in result)


def test_analyze_endpoint_returns_result():
    client = TestClient(app)
    response = client.post("/analyze", json={"text": "Urgent! Verify your account now and pay the processing fee immediately."})

    assert response.status_code == 200
    payload = response.json()
    assert payload["risk_level"] in {"LOW", "MEDIUM", "HIGH"}
    assert payload["risk_score"] > 0
    assert len(payload["signals"]) > 0

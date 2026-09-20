"""AWS Lambda entrypoint for API Gateway HTTP API."""

import json
import os
from typing import Any, Dict

from app.agent import analyze_with_agent, persist_analysis


def _response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": os.getenv("ALLOWED_ORIGIN", "*"),
            "Access-Control-Allow-Headers": "content-type",
        },
        "body": json.dumps(body),
    }


def handler(event: Dict[str, Any], _context: Any) -> Dict[str, Any]:
    if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return _response(204, {})

    try:
        raw_body = event.get("body") or "{}"
        payload = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
        text = str(payload.get("text", "")).strip()
        max_length = int(os.getenv("MAX_INPUT_LENGTH", "10000"))
        if not text:
            return _response(400, {"detail": "Input text cannot be empty."})
        if len(text) > max_length:
            return _response(413, {"detail": f"Input text exceeds {max_length} characters."})

        result = analyze_with_agent(text)
        persist_analysis(result)
        return _response(200, result)
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        return _response(400, {"detail": str(exc)})
    except Exception:
        return _response(500, {"detail": "An unexpected server error occurred."})

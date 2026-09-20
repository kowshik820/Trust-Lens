import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "")
PORT = int(os.getenv("PORT", "8001"))
MAX_INPUT_LENGTH = int(os.getenv("MAX_INPUT_LENGTH", "10000"))

_DEFAULT_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
ALLOWED_ORIGINS = _parse_csv(os.getenv("ALLOWED_ORIGINS")) or _DEFAULT_ALLOWED_ORIGINS

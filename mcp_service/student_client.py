import os
from typing import Dict

import httpx


STUDENT_SERVICE_BASE_URL = os.getenv(
    "STUDENT_SERVICE_BASE_URL",
    "http://127.0.0.1:8001",
).rstrip("/")
STUDENT_SERVICE_TIMEOUT_SECONDS = float(os.getenv("STUDENT_SERVICE_TIMEOUT_SECONDS", "5"))


def fetch_student_service_json(path: str) -> Dict:
    url = f"{STUDENT_SERVICE_BASE_URL}{path}"

    try:
        response = httpx.get(url, timeout=STUDENT_SERVICE_TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as exc:
        return {
            "error": "student_service_request_failed",
            "url": url,
            "detail": str(exc),
        }

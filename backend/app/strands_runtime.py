"""Optional Strands Agent runtime adapter.

The deterministic tools remain the local fallback. When strands-agents is installed,
this module provides the named agent boundary used by the AWS deployment.
"""

from typing import Any, Optional

try:
    from strands import Agent
except ImportError:  # Local development does not require the cloud agent package.
    Agent = None  # type: ignore[assignment]


def create_strands_agent() -> Optional[Any]:
    if Agent is None:
        return None
    return Agent(
        name="trustlens-risk-agent",
        system_prompt=(
            "You are TrustLens. Coordinate URL, email, and job-scam analysis tools. "
            "Report observed evidence and uncertainty; never claim certainty of fraud."
        ),
    )

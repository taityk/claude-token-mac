"""Scraper for claude.ai usage data.

Two-step flow:
1. GET /api/account → extract org_uuid (cached after first successful fetch)
2. GET /api/organizations/{org_uuid}/usage → parse utilization data

All errors (network, auth, parse) produce UsageStatus.unknown().
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import threading

import requests

from models import State, UsageStatus

_BASE = "https://claude.ai"

# Module-level cache so we only call /api/account once per process.
_org_uuid: Optional[str] = None
_org_uuid_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _make_session(session_cookie: str) -> requests.Session:
    """Create and configure a requests session with authentication."""
    session = requests.Session()
    session.cookies.set("sessionKey", session_cookie, domain="claude.ai")
    session.headers.update({
        "Accept": "application/json",
        "User-Agent": "claude-token-mac/1.0",
    })
    return session


def _get_org_uuid(session: requests.Session) -> Optional[str]:
    """Fetch org UUID from /api/account, caching the result."""
    global _org_uuid
    with _org_uuid_lock:
        if _org_uuid:
            return _org_uuid
    # fetch outside lock to avoid holding it during network call
    resp = session.get(f"{_BASE}/api/account", timeout=10)
    if not resp.ok:
        return None
    data = resp.json()
    try:
        uuid = data["memberships"][0]["organization"]["uuid"]
    except (KeyError, IndexError):
        return None
    with _org_uuid_lock:
        _org_uuid = uuid
    return uuid


def _get(session: requests.Session, org_uuid: str) -> requests.Response:
    """Make authenticated request to the usage endpoint."""
    return session.get(
        f"{_BASE}/api/organizations/{org_uuid}/usage",
        timeout=10,
    )


def _parse_response(data: dict, warning_threshold: int) -> UsageStatus:
    """Parse /api/organizations/{org}/usage response into UsageStatus.

    Raises KeyError / ValueError if the payload is malformed.
    """
    five_hour = data["five_hour"]
    utilization: float = float(five_hour["utilization"])
    resets_at_raw: str = five_hour["resets_at"]

    remaining = int(100 - utilization)
    reset_at = datetime.fromisoformat(resets_at_raw)

    if utilization >= 100:
        state = State.LIMITED
    elif remaining <= warning_threshold:
        state = State.WARNING
    else:
        state = State.NORMAL

    return UsageStatus(
        state=state,
        remaining=remaining,
        reset_at=reset_at,
        fetched_at=datetime.now(tz=timezone.utc),
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def fetch_usage(session_cookie: str, warning_threshold: int) -> UsageStatus:
    """Fetch and parse claude.ai usage status.

    Returns UsageStatus.unknown() on any error (auth failure, network error,
    unexpected payload shape).
    """
    try:
        # Build session once and reuse for both API calls
        session = _make_session(session_cookie)

        # Step 1: resolve org UUID (uses cached value after first call).
        org_uuid = _get_org_uuid(session)
        if org_uuid is None:
            return UsageStatus.unknown()

        # Step 2: fetch usage data.
        resp = _get(session, org_uuid)
        if not resp.ok:
            return UsageStatus.unknown()

        data = resp.json()
        return _parse_response(data, warning_threshold)

    except Exception:  # network errors, parse errors, anything else
        return UsageStatus.unknown()

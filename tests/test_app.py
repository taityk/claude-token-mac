# tests/test_app.py
from datetime import datetime, timedelta, timezone
from models import State, UsageStatus
from app import format_title

def test_format_title_normal():
    s = UsageStatus(State.NORMAL, remaining=88, reset_at=None, fetched_at=datetime.now())
    assert format_title(s) == "◆ 88%"

def test_format_title_warning():
    s = UsageStatus(State.WARNING, remaining=15, reset_at=None, fetched_at=datetime.now())
    assert format_title(s) == "◆ 15%"

def test_format_title_limited_shows_countdown():
    reset = datetime.now(timezone.utc) + timedelta(hours=2, minutes=14, seconds=33)
    s = UsageStatus(State.LIMITED, remaining=0, reset_at=reset, fetched_at=datetime.now())
    title = format_title(s)
    # Must be "◆ 2:14:33" format (h:mm:ss) — allow ±1 second for test timing
    assert title.startswith("◆ 2:14:")
    parts = title.split(":")
    assert len(parts) == 3

def test_format_title_unknown():
    assert format_title(UsageStatus.unknown()) == "◆ ?"

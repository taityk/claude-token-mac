from datetime import datetime, timedelta
from models import State, UsageStatus

def test_state_values_exist():
    assert State.NORMAL
    assert State.WARNING
    assert State.LIMITED
    assert State.UNKNOWN

def test_usage_status_normal():
    s = UsageStatus(state=State.NORMAL, remaining=42, reset_at=None, fetched_at=datetime.now())
    assert s.remaining == 42
    assert s.reset_at is None

def test_usage_status_limited():
    reset = datetime.now() + timedelta(hours=2, minutes=14)
    s = UsageStatus(state=State.LIMITED, remaining=0, reset_at=reset, fetched_at=datetime.now())
    assert s.state == State.LIMITED
    assert s.reset_at == reset

def test_usage_status_unknown_factory():
    s = UsageStatus.unknown()
    assert s.state == State.UNKNOWN
    assert s.remaining is None
    assert s.reset_at is None

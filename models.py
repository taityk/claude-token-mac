from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Optional

class State(Enum):
    NORMAL = auto()
    WARNING = auto()
    LIMITED = auto()
    UNKNOWN = auto()

@dataclass
class UsageStatus:
    state: State
    remaining: Optional[int]
    reset_at: Optional[datetime]
    fetched_at: datetime

    @classmethod
    def unknown(cls) -> UsageStatus:
        return cls(state=State.UNKNOWN, remaining=None, reset_at=None, fetched_at=datetime.now())

import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".config" / "claude-token-mac" / "config.json"


class Config:
    def __init__(self):
        self.warning_threshold: int = 10
        self.poll_interval_minutes: int = 5
        self._load()

    def _load(self):
        if CONFIG_PATH.exists():
            data = json.loads(CONFIG_PATH.read_text())
            self.warning_threshold = data.get("warning_threshold", 10)
            self.poll_interval_minutes = data.get("poll_interval_minutes", 5)

    def save(self):
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(json.dumps({
            "warning_threshold": self.warning_threshold,
            "poll_interval_minutes": self.poll_interval_minutes,
        }, indent=2))

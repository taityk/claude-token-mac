from pathlib import Path
from unittest.mock import patch
from config import Config


def test_default_values():
    with patch('config.CONFIG_PATH', Path('/tmp/nonexistent_config.json')):
        c = Config()
    assert c.warning_threshold == 10
    assert c.poll_interval_minutes == 5


def test_save_and_load(tmp_path):
    config_path = tmp_path / "config.json"
    with patch('config.CONFIG_PATH', config_path):
        c = Config()
        c.warning_threshold = 15
        c.save()
        c2 = Config()
        assert c2.warning_threshold == 15

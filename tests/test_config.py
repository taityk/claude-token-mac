from pathlib import Path
from unittest.mock import patch
from config import Config


def test_default_values():
    with patch('keyring.get_password', return_value=None):
        with patch('config.CONFIG_PATH', Path('/tmp/nonexistent_config.json')):
            c = Config()
    assert c.warning_threshold == 10
    assert c.poll_interval_minutes == 5


def test_save_and_load(tmp_path):
    config_path = tmp_path / "config.json"
    with patch('config.CONFIG_PATH', config_path):
        with patch('keyring.get_password', return_value=None):
            c = Config()
            c.warning_threshold = 15
            c.save()
            c2 = Config()
            assert c2.warning_threshold == 15


def test_get_session_cookie():
    with patch('keyring.get_password', return_value="my-session-token"):
        with patch('config.CONFIG_PATH', Path('/tmp/nonexistent_config.json')):
            c = Config()
            assert c.get_session_cookie() == "my-session-token"


def test_set_session_cookie():
    with patch('keyring.set_password') as mock_set:
        with patch('keyring.get_password', return_value=None):
            with patch('config.CONFIG_PATH', Path('/tmp/nonexistent_config.json')):
                c = Config()
                c.set_session_cookie("new-token")
                mock_set.assert_called_once_with(
                    "claude-token-mac", "session_cookie", "new-token"
                )

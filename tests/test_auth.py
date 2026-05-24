from unittest.mock import patch
from auth import AuthManager

def test_is_logged_in_true():
    with patch("auth.keyring.get_password", return_value="some-cookie"):
        assert AuthManager().is_logged_in() is True

def test_is_logged_in_false():
    with patch("auth.keyring.get_password", return_value=None):
        assert AuthManager().is_logged_in() is False

def test_get_cookie():
    with patch("auth.keyring.get_password", return_value="abc123"):
        assert AuthManager().get_cookie() == "abc123"

def test_login_calls_login_window(mocker):
    mock_main = mocker.patch("login_window.main")
    AuthManager().login()
    mock_main.assert_called_once()

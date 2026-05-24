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

def test_login_launches_subprocess(mocker):
    mock_popen = mocker.patch("auth.subprocess.Popen")
    mock_popen.return_value.wait.return_value = 0
    AuthManager().login()
    mock_popen.assert_called_once()
    args = mock_popen.call_args[0][0]
    assert "login_window.py" in args[-1]

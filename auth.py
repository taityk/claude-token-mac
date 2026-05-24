import keyring
import subprocess
import sys
import time
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

KEYRING_SERVICE = "claude-token-mac"
KEYRING_COOKIE_KEY = "session_cookie"
LOGIN_WINDOW = Path(__file__).parent / "login_window.py"

class AuthManager:
    def is_logged_in(self) -> bool:
        return bool(keyring.get_password(KEYRING_SERVICE, KEYRING_COOKIE_KEY))

    def get_cookie(self) -> Optional[str]:
        return keyring.get_password(KEYRING_SERVICE, KEYRING_COOKIE_KEY)

    def login(self):
        logger.info("Launching login window")
        proc = subprocess.Popen([sys.executable, str(LOGIN_WINDOW)])
        proc.wait()
        # Poll until cookie appears (up to 2 seconds)
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline:
            if self.is_logged_in():
                break
            time.sleep(0.1)

    def logout(self):
        try:
            keyring.delete_password(KEYRING_SERVICE, KEYRING_COOKIE_KEY)
        except keyring.errors.PasswordDeleteError:
            pass

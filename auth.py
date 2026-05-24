import keyring
import logging
from typing import Optional

from constants import KEYRING_SERVICE, KEYRING_COOKIE_KEY

logger = logging.getLogger(__name__)


class AuthManager:
    def is_logged_in(self) -> bool:
        return bool(keyring.get_password(KEYRING_SERVICE, KEYRING_COOKIE_KEY))

    def get_cookie(self) -> Optional[str]:
        return keyring.get_password(KEYRING_SERVICE, KEYRING_COOKIE_KEY)

    def login(self):
        """Run pywebview login window. Must be called before rumps event loop starts."""
        logger.info("Starting login window")
        from login_window import main as run_login_window
        run_login_window()

    def logout(self):
        try:
            keyring.delete_password(KEYRING_SERVICE, KEYRING_COOKIE_KEY)
        except keyring.errors.PasswordDeleteError:
            pass

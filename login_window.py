#!/usr/bin/env python3
"""Standalone login window — launched as subprocess by auth.py."""
import keyring
import threading
import webview

from constants import KEYRING_SERVICE, KEYRING_COOKIE_KEY


def main():
    def poll_for_login():
        """Poll URL and cookies every second until logged in."""
        while True:
            try:
                url = win.get_current_url() or ""
                if (url.startswith("https://claude.ai/")
                        and "login" not in url
                        and "sign" not in url):
                    cookies = win.get_cookies()
                    token = None
                    for cookie in cookies:
                        if "sessionKey" in cookie:
                            token = cookie["sessionKey"].value
                            break
                    if token:
                        keyring.set_password(KEYRING_SERVICE, KEYRING_COOKIE_KEY, token)
                        win.destroy()
                        return
            except Exception:
                pass
            threading.Event().wait(1.0)

    win = webview.create_window(
        "Claude.ai にログイン",
        "https://claude.ai/login",
        width=960,
        height=720,
    )
    webview.start(poll_for_login)


if __name__ == "__main__":
    main()

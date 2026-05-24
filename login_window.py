#!/usr/bin/env python3
"""Standalone login window — launched as subprocess by auth.py."""
import keyring
import webview

from constants import KEYRING_SERVICE, KEYRING_COOKIE_KEY

def main():
    def on_loaded():
        url = win.get_current_url() or ""
        if (url.startswith("https://claude.ai/")
                and "login" not in url
                and "sign" not in url):
            cookies = win.get_cookies()
            token = next(
                (c["value"] for c in cookies if c.get("name") == "sessionKey"),
                None,
            )
            if token:
                keyring.set_password(KEYRING_SERVICE, KEYRING_COOKIE_KEY, token)
                win.destroy()

    win = webview.create_window(
        "Claude.ai にログイン",
        "https://claude.ai/login",
        width=960,
        height=720,
    )
    win.events.loaded += on_loaded
    webview.start()

if __name__ == "__main__":
    main()

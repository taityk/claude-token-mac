# Privacy Policy — TokenBar

Last updated: May 25, 2026

## Information We Collect

TokenBar collects and stores only the following information:

**Session Cookie (`sessionKey`)**
A session identifier issued by Claude.ai after you sign in. It is stored exclusively in the macOS Keychain on your device and is never transmitted anywhere other than back to claude.ai.

## Information We Do Not Collect

TokenBar does not collect, store, or transmit:

- Personal information such as your name or email address
- Conversation content or any text you enter into Claude.ai
- Location data
- Crash reports or diagnostic data
- Usage analytics or telemetry of any kind

## Network Communication

TokenBar communicates only with claude.ai, specifically the following endpoints:

- `https://claude.ai/api/account` — to retrieve your organization identifier
- `https://claude.ai/api/organizations/{id}/usage` — to retrieve your current usage status

All requests are made using the session cookie you have stored. Anthropic's Terms of Service and Privacy Policy apply to these requests.

## Data Storage

All data remains on your Mac.

- Session cookie: macOS Keychain
- Settings (refresh interval, warning threshold): `~/.config/tokenbar/config.json`

## Deleting Your Data

Uninstalling the app removes the settings file. To remove the Keychain entry, use the "Re-login" menu item (which clears the stored cookie) or search for `claude-token-mac` in the macOS Keychain Access app.

## Contact

For questions or concerns, please open an issue on GitHub:
https://github.com/taityk/claude-token-mac/issues

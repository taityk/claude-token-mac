import logging
import threading
import rumps
from datetime import datetime, timezone
from typing import Optional

from models import State, UsageStatus
from config import Config
from scraper import fetch_usage
from auth import AuthManager

logger = logging.getLogger(__name__)


def format_title(status: UsageStatus) -> str:
    if status.state == State.LIMITED and status.reset_at:
        reset = status.reset_at
        if reset.tzinfo is None:
            reset = reset.replace(tzinfo=timezone.utc)
        secs = max(0, int((reset - datetime.now(timezone.utc)).total_seconds()))
        h, rem = divmod(secs, 3600)
        m, s = divmod(rem, 60)
        return f"◆ {h}:{m:02d}:{s:02d}"
    if status.state in (State.NORMAL, State.WARNING) and status.remaining is not None:
        return f"◆ {status.remaining}%"
    return "◆ ?"


class ClaudeTokenApp(rumps.App):
    def __init__(self):
        super().__init__("◆ …", quit_button=None)
        self._config = Config()
        self._auth = AuthManager()
        self._status: Optional[UsageStatus] = None
        self._last_fetch: Optional[datetime] = None

        self._remaining_item = rumps.MenuItem("使用率: 読込中")
        self._updated_item = rumps.MenuItem("更新: —")

        self.menu = [
            rumps.MenuItem("Claude.ai 使用状況"),
            rumps.separator,
            self._remaining_item,
            self._updated_item,
            rumps.separator,
            rumps.MenuItem("今すぐ更新", callback=self.refresh),
            rumps.MenuItem("設定...", callback=self.open_settings),
            rumps.MenuItem("再ログイン", callback=self.relogin),
            rumps.separator,
            rumps.MenuItem("終了", callback=self.quit_app),
        ]

    def run(self):
        if not self._auth.is_logged_in():
            self._auth.login()
        threading.Thread(target=self._do_fetch, daemon=True).start()
        super().run()

    def _do_fetch(self):
        cookie = self._auth.get_cookie()
        if not cookie:
            self._status = UsageStatus.unknown()
        else:
            self._status = fetch_usage(cookie, self._config.warning_threshold)
            if self._status.state == State.UNKNOWN:
                rumps.notification(
                    "Claude Token", "", "データ取得に失敗。再ログインが必要な場合があります。"
                )
        self._last_fetch = datetime.now()
        self._update_display()

    @rumps.timer(60)
    def maybe_poll(self, _):
        if self._last_fetch is None:
            return
        elapsed = (datetime.now() - self._last_fetch).total_seconds()
        if elapsed >= self._config.poll_interval_minutes * 60:
            threading.Thread(target=self._do_fetch, daemon=True).start()

    @rumps.timer(1)
    def tick(self, _):
        if self._status and self._status.state == State.LIMITED:
            self._update_display()

    def _update_display(self):
        if not self._status:
            return
        title = format_title(self._status)
        self._set_colored_title(title, self._status.state)

        if self._status.remaining is not None:
            self._remaining_item.title = f"5時間枠: {self._status.remaining}% 残り"
        else:
            self._remaining_item.title = "使用率: 不明"

        if self._last_fetch:
            self._updated_item.title = f"更新: {self._relative_time(self._last_fetch)}"

    def _set_colored_title(self, text: str, state: State):
        if not hasattr(self, '_status_item'):
            return
        from AppKit import NSAttributedString, NSForegroundColorAttributeName, NSColor
        colors = {
            State.NORMAL: NSColor.labelColor(),
            State.WARNING: NSColor.systemOrangeColor(),
            State.LIMITED: NSColor.systemRedColor(),
            State.UNKNOWN: NSColor.systemGrayColor(),
        }
        color = colors.get(state, NSColor.labelColor())
        attrs = {NSForegroundColorAttributeName: color}
        attributed = NSAttributedString.alloc().initWithString_attributes_(text, attrs)
        self._status_item.button().setAttributedTitle_(attributed)

    def _relative_time(self, dt: datetime) -> str:
        secs = int((datetime.now() - dt).total_seconds())
        if secs < 60:
            return f"{secs}秒前"
        if secs < 3600:
            return f"{secs // 60}分前"
        return f"{secs // 3600}時間前"

    def refresh(self, _):
        threading.Thread(target=self._do_fetch, daemon=True).start()

    def open_settings(self, _):
        w = rumps.Window(
            message="ポーリング間隔（分）を入力してください",
            default_text=str(self._config.poll_interval_minutes),
            ok="保存",
            cancel="キャンセル",
            dimensions=(200, 20),
        )
        w.title = "Claude Token 設定"
        resp = w.run()
        if resp.clicked == 1:
            try:
                self._config.poll_interval_minutes = int(resp.text)
                self._config.save()
            except ValueError:
                rumps.notification("Claude Token", "入力エラー", "数値を入力してください")

    def relogin(self, _):
        threading.Thread(target=self._do_relogin, daemon=True).start()

    def _do_relogin(self):
        self._auth.login()
        self._do_fetch()

    def quit_app(self, _):
        rumps.quit_application()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ClaudeTokenApp().run()

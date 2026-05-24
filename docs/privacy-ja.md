---
layout: default
title: TokenBar — プライバシーポリシー
---

# プライバシーポリシー — TokenBar

最終更新日：2026年5月25日

## 収集する情報

TokenBar が収集・保存する情報は以下のみです。

**セッション Cookie（`sessionKey`）**
Claude.ai へのログイン後に発行されるセッション識別子です。macOS のキーチェーンにのみ保存され、あなたの Mac の外部に送信されることはありません。

## 収集しない情報

TokenBar は以下の情報を一切収集・送信しません。

- 氏名・メールアドレスなどの個人情報
- 会話内容・入力テキスト
- 位置情報
- クラッシュレポート・診断データ
- 利用統計・分析データ

## 通信先

TokenBar は claude.ai のみと通信します。具体的には以下のエンドポイントです。

- `https://claude.ai/api/account`（所属組織の取得）
- `https://claude.ai/api/organizations/{id}/usage`（使用状況の取得）

これらのリクエストは、あなたが保存したセッション Cookie を使って行われます。Anthropic（Claude.ai 運営会社）の利用規約およびプライバシーポリシーが適用されます。

## データの保存場所

すべてのデータはあなたの Mac 上にのみ保存されます。

- セッション Cookie：macOS キーチェーン
- 設定（更新間隔・警告しきい値）：`~/.config/tokenbar/config.json`

## データの削除

アプリをアンインストールすると、設定ファイルは削除されます。キーチェーンの項目は、「再ログイン」メニューから手動で削除するか、macOS の「キーチェーンアクセス」アプリから `claude-token-mac` を検索して削除できます。

## お問い合わせ

ご質問は GitHub の Issue よりお願いします。
[https://github.com/taityk/claude-token-mac/issues](https://github.com/taityk/claude-token-mac/issues)

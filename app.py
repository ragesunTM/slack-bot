import os
from flask import Flask, request
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import requests

app = Flask(__name__)

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
GAS_ENDPOINT = os.environ["GAS_ENDPOINT"]

client = WebClient(token=SLACK_BOT_TOKEN)

@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json
    print("Received data:", data)  # Slackからの全データを出力

    # URL検証用のchallenge対応（初期設定時にSlackが送信）
    if "challenge" in data:
        return data["challenge"]

    if "event" in data:
        event = data["event"]
        print("Slack Event:", event)

        # 通常のメッセージイベントか確認
        if event.get("type") == "message" and "subtype" not in event:
            channel = event["channel"]
            text = event["text"]
            user = event.get("user")
            ts = event.get("ts")

            try:
                # メッセージ形式: 「店名 | 住所 | コメント」
                lines = text.strip().splitlines()
                if len(lines) >= 3:
                    shop_name = lines[0].strip()
                    phone = lines[1].strip()  # 電話番号は未使用なら無視しても可
                    address = lines[2].strip()
                    comment = lines[3].strip() if len(lines) >= 4 else ""

                    # Slackメッセージリンクを作成
                    ts_formatted = ts.replace(".", "")
                    slack_url = f"https://slack.com/app_redirect?channel={channel}&message_ts={ts}"

                    # GASへ送信するデータ
                    payload = {
                        "shopName": shop_name,
                        "address": address,
                        "comment": comment,
                        "slackUrl": slack_url
                    }

                    res = requests.post(GAS_ENDPOINT, json=payload)
                    print("GAS response:", res.text)
                else:
                    print("メッセージ形式が正しくありません。")

            except Exception as e:
                print("メッセージ解析エラー:", e)

    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

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

    # SlackのURL確認用 challenge 対応
    if "challenge" in data:
        return data["challenge"]

    if "event" in data:
        event = data["event"]
        if event.get("type") == "message" and "subtype" not in event:
            channel = event["channel"]
            text = event["text"]
            user = event.get("user")
            ts = event.get("ts")

            # メッセージを解析（例: 「店名｜住所｜コメント」形式で投稿されている想定）
            try:
                shop_name, address, comment = map(str.strip, text.split("|"))

                slack_url = f"https://slack.com/app_redirect?channel={channel}&message_ts={ts}"

                payload = {
                    "shopName": shop_name,
                    "address": address,
                    "comment": comment,
                    "slackUrl": slack_url
                }

                # GASへPOST
                res = requests.post(GAS_ENDPOINT, json=payload)
                print("GAS response:", res.text)

            except Exception as e:
                print("メッセージ解析エラー:", e)

    return "ok", 200

if __name__ == "__main__":
    app.run(port=3000)

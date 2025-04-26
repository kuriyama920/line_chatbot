from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from openai import OpenAI
import os

app = Flask(__name__)

# 環境変数から読み込み
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "あなたのアクセストークン")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "あなたのシークレット")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "あなたのOpenAIキー")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# OpenAIのクライアントを初期化（ここが新しい書き方！）
client = OpenAI(api_key=OPENAI_API_KEY)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text

    # ChatGPTに投げる（新しい呼び出し方）
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # or gpt-4
        messages=[
            {"role": "user", "content": user_message}
        ]
    )

    reply = response.choices[0].message.content.strip()

    # LINEに返信
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, abort
from linebot import WebhookHandler, LineBotApi  # 正しいインポート方法
from linebot.exceptions import InvalidSignatureError  # 例外処理のインポート
from linebot.models import MessageEvent, TextMessage, TextSendMessage  # メッセージ関連のインポート
import openai
import os

app = Flask(__name__)

# 環境変数から読み込み
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "あなたのアクセストークン")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "あなたのシークレット")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "あなたのOpenAIキー")

# LINE SDKの初期化
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)  # 正しいクラスの初期化
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# OpenAIのクライアントを初期化
openai.api_key = OPENAI_API_KEY

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
    # とりあえずChatGPTなしで動作確認する
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="こんにちは！こちらはテスト返信です。")
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

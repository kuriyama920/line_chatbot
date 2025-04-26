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
    user_message = event.message.text  # 受け取ったメッセージ

    try:
        # OpenAI APIの呼び出し（修正後）
        response = openai.Completion.create(
            model="gpt-3.5-turbo",  # または "gpt-4"
            prompt=user_message,  # ユーザーからのメッセージを送信
            max_tokens=150  # トークン制限を設定（必要に応じて調整）
        )

        # ChatGPTからの返答を取得
        reply = response['choices'][0]['text'].strip()  # 'text' を使用

        # LINEに返信
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)  # ChatGPTからの返答をLINEに送信
        )

    except openai.OpenAIError as e:
        print(f"OpenAI API Error: {e}")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="申し訳ありませんが、エラーが発生しました。")
        )
    except Exception as e:
        print(f"Error: {e}")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="予期しないエラーが発生しました。")
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

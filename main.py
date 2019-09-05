# coding: utf-8
# author pet_sensei

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage,
    ImageMessage, VideoMessage, AudioMessage
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot import (
    LineBotApi, WebhookHandler
)
from flask import Flask, request, abort, send_from_directory
from io import BytesIO
import json
import os
import sys
import tempfile
import errno
import logging

# loglevelの設定。
logging.getLogger().setLevel(logging.DEBUG)

# Flaskを使用
app = Flask(__name__)

# API設定。環境変数からLINEMESSAGEAPI用のパラメータを取得して設定する。
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

# パラメータが設定されていな場合はエラーメッセージを出力して落とす。
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

# LINEBOTのインスタンスを生成
line_bot_api = LineBotApi(channel_access_token)
# LINEアプリのWebhookインスタンスを生成
handler = WebhookHandler(channel_secret)


@app.route("/")
def hello():
    """
    ルートにアクセスされた場合の処理を記述
    エラーメッセージを表示する。
    """
    app.logger.info("route access hello this page is nothing.")
    return "hello this page is nothing."


@app.route("/callback", methods=['POST'])
def callback():
    """ 
    Webhookに登録するアドレス。
    ラインでメッセージが送られてきた場合の処理を記述する。
    """
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """ 
    テキストメッセージが送られた場合の処理
    """
    app.logger.debug("handle_message")

    text = event.message.text
    message_text = "「予約」と入力してください。"
    if text == "予約":
        message_text = "予約します。"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message_text))

# Other Message Type


@handler.add(MessageEvent, message=(ImageMessage, VideoMessage, AudioMessage))
def handle_content_message(event):
    """ 
    画像、動画、音声が送られた場合の処理
    """

    try:
        app.logger.debug("handle_content_message")

        message_content = line_bot_api.get_message_content(event.message.id)
        message_text = "画像には対応していません。"


        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text=message_text)
            ])

    except Exception as e:
        app.logger.error(e)


if __name__ == "__main__":
    app.run()

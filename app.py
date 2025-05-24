from flask import Flask, request
from bs4 import BeautifulSoup
import requests
import os
from linebot import LineBotApi
from linebot.v3.webhook import WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# --- 功能：抓取中獎號碼 ---
def bug(x):
    span = ''
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
    }
    url = 'https://invoice.etax.nat.gov.tw/index.html'
    web = requests.get(url, timeout=5, headers=headers)
    web.encoding = 'utf-8'

    soup = BeautifulSoup(web.text, "html.parser")
    ta = soup.find('table', class_="etw-table-bgbox etw-tbig").find_all('span', class_="font-weight-bold etw-color-red")
    tan = soup.find('p', class_="etw-tbiggest mb-md-4")
    tanb = tan.find_next_siblings()

    print(ta[0].get_text())
    print(ta[1].get_text())
    print(tan.get_text()[-8:])
    print(tanb[0].get_text()[-8:])
    print(tanb[1].get_text()[-8:])

    if x == 0:
        span = ta[0].get_text()
    elif x == 1:
        span = ta[1].get_text()
    elif x == 2:
        span = tan.get_text()[-8:]
    elif x == 3:
        span = tanb[0].get_text()[-8:]
    elif x == 4:
        span = tanb[1].get_text()[-8:]

    return span

# --- 讀取環境變數 ---
access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
secret = os.getenv("LINE_CHANNEL_SECRET")

if access_token is None or secret is None:
    raise ValueError("請確認環境變數 LINE_CHANNEL_ACCESS_TOKEN 和 LINE_CHANNEL_SECRET 已設定")

# --- 初始化 LINE API ---
line_bot_api = LineBotApi(access_token)
handler = WebhookHandler(secret)

# --- 啟動時預抓中獎號碼 ---
award_a = bug(0)
award_b = bug(1)
award_c = bug(2)
award_d = bug(3)
award_e = bug(4)

# --- 根路徑測試（避免 Method Not Allowed）---
@app.route("/", methods=['GET'])
def home():
    return "Hello, this is the LINE Bot Server!", 200

# --- 處理 Webhook ---
@app.route("/", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True)
    signature = request.headers.get('X-Line-Signature')

    try:
        handler.handle(body, signature)

        json_data = request.get_json()
        event = json_data['events'][0]
        reply_token = event['replyToken']
        message_type = event['message']['type']

        if message_type == 'text':
            msg = event['message']['text']
            omsg = check_lottery(msg)
        else:
            omsg = '你傳的不是文字訊息'

        line_bot_api.reply_message(reply_token, TextSendMessage(text=omsg))
    except InvalidSignatureError:
        return 'Invalid signature', 400
    except Exception as e:
        print(f"Error: {e}")
        return 'Internal Server Error', 500

    return 'OK', 200

# --- 處理發票對獎邏輯 ---
def check_lottery(msg):
    if len(msg) >= 3 and msg.isdigit():
        if msg == award_a:
            return "🎉 恭喜中獎! 特別獎 1,000萬元!"
        elif msg == award_b:
            return "🎉 恭喜中獎! 特獎 200萬元!"
        elif msg in [award_c, award_d, award_e]:
            return "🎉 恭喜中獎! 頭獎 20萬元!"
        elif msg[-7:] in [award_c[-7:], award_d[-7:], award_e[-7:]]:
            return "🎉 恭喜中獎! 二獎 4萬元!"
        elif msg[-6:] in [award_c[-6:], award_d[-6:], award_e[-6:]]:
            return "🎉 恭喜中獎! 三獎 1萬元!"
        elif msg[-5:] in [award_c[-5:], award_d[-5:], award_e[-5:]]:
            return "🎉 恭喜中獎! 四獎 4千元!"
        elif msg[-4:] in [award_c[-4:], award_d[-4:], award_e[-4:]]:
            return "🎉 恭喜中獎! 五獎 1千元!"
        elif msg[-3:] in [award_c[-3:], award_d[-3:], award_e[-3:]]:
            return "🎉 恭喜中獎! 六獎 2百元!"
        else:
            return "😢 可惜! 沒中獎..."
    else:
        return "請輸入正確的發票號碼（至少3碼的數字）"

# --- 執行應用 ---
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

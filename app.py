from flask import Flask, request
from bs4 import BeautifulSoup
import requests
import json
import os

def bug(x):
    span = 0
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
    url = 'https://invoice.etax.nat.gov.tw/index.html'
    web = requests.get(url,timeout= 5,headers=headers)    # 取得網頁內容
    web.encoding='utf-8'       # 因為該網頁編碼為 utf-8，加上 .encoding 避免亂碼

    soup=BeautifulSoup(web.text,"html.parser")

    ta=soup.find('table',class_="etw-table-bgbox etw-tbig").find_all('span',class_="font-weight-bold etw-color-red")
    tan=soup.find('p',class_="etw-tbiggest mb-md-4")
    tanb=tan.find_next_siblings()

    if x == 0:
        span = ta[0].get_text()

    elif x ==1:
        span = ta[1].get_text()

    elif x ==2:
        span = tan.get_text()[-8:]

    elif x ==3:
        span = tanb[0].get_text()[-8:]

    elif x ==4:
        span = tanb[1].get_text()[-8:]

    return span

# 更新為使用 v3 模組（新的導入方式）
from linebot import LineBotApi
from linebot.v3.webhook import WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# 您的 LINE Channel 的 access token 和 secret
access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
secret = os.getenv("LINE_CHANNEL_SECRET")

# 實例化 LineBotApi 和 WebhookHandler
line_bot_api = LineBotApi(access_token)
handler = WebhookHandler(secret)

@app.route("/", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True)  # 取得原始的 webhook 資料
    signature = request.headers['X-Line-Signature']  # 取得簽名

    a=bug(0)

    b=bug(1)

    c=bug(2)

    d=bug(3)

    e=bug(4)

    try:
        # 驗證簽名並處理事件
        handler.handle(body, signature)

        # 解析收到的事件
        json_data = request.get_json()

        # 取得 replyToken 和收到的訊息內容
        tk = json_data['events'][0]['replyToken']
        msg_type = json_data['events'][0]['message']['type']

        # 若是文字訊息，則回覆相同訊息
        if msg_type == 'text':
            msg = json_data['events'][0]['message']['text']  # 取得文字訊息

            if len(msg)>=3 and msg.isdigit():
                if msg==a:
                    omsg="恭喜中獎!特別獎 1,000萬元!"
                elif msg==b:
                    omsg="恭喜中獎!特獎 200萬元!"
                elif msg==c or msg==d or msg==e:
                     omsg="恭喜中獎!頭獎 20萬元!"
                elif msg[-7:]==c[-7:] or msg[-7:]==d[-7:] or msg[-7:]==e[-7:]:
                    omsg="恭喜中獎!二獎 4萬元!"
                elif msg[-6:]==c[-6:] or msg[-6:]==d[-6:] or msg[-6:]==e[-6:]:
                    omsg="恭喜中獎!三獎 1萬元!"
                elif msg[-5:]==c[-5:] or msg[-5:]==d[-5:] or msg[-5:]==e[-5:]:
                    omsg="恭喜中獎!四獎 4千元!"
                elif msg[-4:]==c[-4:] or msg[-4:]==d[-4:] or msg[-4:]==e[-4:]:
                    omsg="恭喜中獎!五獎 1千元!"
                elif msg[-3:]==c[-3:] or msg[-3:]==d[-3:] or msg[-3:]==e[-3:]:
                    omsg="恭喜中獎!六獎 2百元!"
                else:
                    omsg='可惜!沒中獎...'
            else:
                    omsg="數字小於3碼或非數字字元。"
        else:
            omsg = '你傳的不是文字訊息'

        # 回覆訊息
        reply = omsg
        line_bot_api.reply_message(tk, TextSendMessage(text=reply))

    except InvalidSignatureError:
        # 驗證簽名失敗
        return 'Invalid signature', 400
    except Exception as e:
        # 發生錯誤，印出錯誤訊息並返回 500
        print(f"Error: {e}")
        return 'Internal Server Error', 500

    return 'OK'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

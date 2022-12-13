import os
import sys
from transitions.extensions import GraphMachine

from utils import send_text_message
from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
#LineBot所需要的套件	
from linebot.exceptions import (	
    InvalidSignatureError	
)	
from linebot.models import *

load_dotenv()

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)
        # print("Test!")
        self.items=[]
        # self.columns=[]
        # self.jishobutton = QuickReplyButton(
        #             action=PostbackAction(label="英日字典", data = "英日字典", text = "英日字典")
        # )
        # items.append(self.jishobutton)
        # self.engbutton = QuickReplyButton(
        #     action=PostbackAction(label="英英字典",data="英英字典", text = "英英字典")
        # )
        # items.append(self.engbutton)
        # self.srcbutton = QuickReplyButton(
        #     action=PostbackAction(label="查看機器人介紹",data="機器人的資料來源", text = "查看機器人資料")
        # )
        # items.append(self.srcbutton)
        greeting_text = """
            嗨囉~\n
            我可以幫你決定早餐或晚餐要吃什麼喔！\n
            可以透過快速回覆按鈕省下打字的時間喔！\n
            輸入\n【英英字典】\n【英日字典】\n進入字典模式！
        """
        self.message = TextSendMessage(
            text="""嗨你好~\n
            我是機器人Leo\n
            我可以讓您方便快速的查詢英日語名詞解釋以及發音！\n
            可以透過快速回覆按鈕省下打字的時間喔！\n
            輸入\n【英英字典】\n【英日字典】\n進入字典模式！""",
            # quick_reply=QuickReply(
            #     items=items
            #
            #  )
        )
        # line_bot_api.reply_message(reply_token,self.message)

    def is_going_to_greeting(self, event):
        text = event.message.text
        return text == "Hi"

    def is_going_to_state1(self, event):
        text = event.message.text
        return text.lower() == "go to state1"

    def is_going_to_state2(self, event):
        text = event.message.text
        return text.lower() == "go to state2"
    
    def is_going_to_state3(self, event):
        text = event.message.text
        return text.lower() == "go to state3"

    def on_enter_greeting(self, event):
        print("I'm entering greeting")
        reply_token = event.reply_token
        # send_text_message(reply_token, "Trigger greeting")
        self.breakfastbutton = QuickReplyButton(
            action=PostbackAction(label="找早餐",data="找早餐", text = "找早餐")
        )
        self.items.append(self.breakfastbutton)
        self.lunchbutton = QuickReplyButton(
            action=PostbackAction(label="找晚餐",data="找晚餐", text = "找晚餐")
        )
        self.items.append(self.lunchbutton)
        self.randombutton = QuickReplyButton(
            action=PostbackAction(label="隨便吃",data="隨便吃", text = "隨便吃")
        )
        self.items.append(self.randombutton)
        self.message = TextSendMessage(
            text="""
嗨囉~\n
我是機器人哲哥\n
我可以幫你決定早餐或晚餐要吃什麼喔！\n
你可以透過下面選單點選或是直接按快速回復按鈕來開始\n
讓你不再為了要吃什麼而煩惱~\n
            """,
            quick_reply=QuickReply(
                items=self.items
            
            ),
        )
        line_bot_api.reply_message(reply_token, self.message)
        self.go_back()

    def on_exit_greeting(self):
        print("Leaving greeting")

    def on_enter_state1(self, event):
        print("I'm entering state1")

        reply_token = event.reply_token
        # send_text_message(reply_token, "Trigger state1")
        sticker_message = StickerSendMessage(	
            package_id='446',	
            sticker_id='1988'	
        )	
        line_bot_api.reply_message(reply_token, sticker_message)
        self.go_back()

    def on_exit_state1(self):
        print("Leaving state1")

    def on_enter_state2(self, event):
        print("I'm entering state2")

        reply_token = event.reply_token
        send_text_message(reply_token, "Trigger state2")
        self.go_back()

    def on_exit_state2(self):
        print("Leaving state2")

    def on_enter_state3(self, event):
        print("I'm entering state3")

        reply_token = event.reply_token
        send_text_message(reply_token, "Trigger state3")
        self.go_back()

    def on_exit_state3(self):
        print("Leaving state3")

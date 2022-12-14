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
# Google Map API
import requests
import urllib.request
import json
import time
import random
load_dotenv()

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
Google_Map_API_KEY = os.getenv("GOOGLE_MAP_API_KEY", None)
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
        # get_location('台南市東區中華東路三段380巷1號1')

        ### get lat and lng
        address = urllib.request.quote('成功大學')
        url = "https://maps.googleapis.com/maps/api/geocode/json?address=" + address + '&key='+ Google_Map_API_KEY

        while True:
            res = requests.get(url)
            js = json.loads(res.text)

            if js['status'] != "OVER_QUERY_LIMIT":
                time.sleep(1)
                break

        result = js['results'][0]["geometry"]["location"]
        lat = result["lat"]
        lng = result["lng"]
        print(lat, lng)
        ###
        ### nearby restaurants
        foodStoreSearch = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?key={}&location={},{}&rankby=distance&type=restaurant&language=zh-TW".format(Google_Map_API_KEY, lat, lng)
        foodReq = requests.get(foodStoreSearch)
        nearby_restaurants_dict = foodReq.json()
        top20_restaurants = nearby_restaurants_dict['results']
        res_num = len(top20_restaurants)
        bravo = []
        for i in range(res_num):
            try:
                if top20_restaurants[i]['rating'] > 3.9:
                    print('rate: ', top20_restaurants[i]['rating'])
                    bravo.append(i)
            except:
                KeyError
        if len(bravo) < 0:
            content = "沒東西可以吃"
            # restaurant = random.choice(top20_restaurants)
        
        restaurant = top20_restaurants[random.choice(bravo)]

        if restaurant.get("photos") is None:
            thumbnail_image_url = None
        else:
            photo_reference = restaurant["photos"][0]["photo_reference"]
            photo_width = restaurant["photos"][0]["width"]
            thumbnail_image_url = "https://maps.googleapis.com/maps/api/place/photo?key={}&photoreference={}&maxwidth={}".format(Google_Map_API_KEY, photo_reference, photo_width)
        
        rating = "無" if restaurant.get("rating") is None else restaurant["rating"]
        address = "沒有資料" if restaurant.get("vicinity") is None else restaurant["vicinity"]
        details = "Google Map評分: {}\n 地址:{}".format(rating, address)
        print(details)

        map_url = "https://www.google.com/maps/search/?api=1&query={lat},{long}&query_place_id={place_id}".format(lat=restaurant["geometry"]["location"]["lat"], long=restaurant["geometry"]["location"]["lng"], place_id= restaurant["place_id"])
        ###
        print("Find Restaurant")
        print("title: ", restaurant['name'])
        ### reply
        # reply_token = event.reply_token
        # send_text_message(reply_token, "Trigger state2")
        # buttons_template = TemplateSendMessage(
        #     alt_text=restaurant["name"],
        #     template=ButtonsTemplate(
        #         thumbnail_image_url = thumbnail_image_url,
        #         title = restaurant['name'],
        #         text = details,
        #         actions=[
        #             URITemplateAction(
        #                 label='查看地圖',
        #                 url=map_url
        #             ),
        #         ]
        #     )
        # )
        # line_bot_api.reply_message(event.reply_token, buttons_template)
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


    def get_location(address):
        address = urllib.request.quote(address)
        url = "https://maps.googleapis.com/maps/api/geocode/json?address=" + address + '&key='+ Google_Map_API_KEY

        while True:
            res = requests.get(url)
            js = json.loads(res.text)

            if js['status'] != "OVER_QUERY_LIMIT":
                time.sleep(1)
                break

        result = js['result'][0]["geometry"]["location"]
        lat = result["lat"]
        lng = result["lng"]
        print(lat, lng)
        return lat, lng


import os
import sys
from transitions.extensions import GraphMachine

from utils import send_text_message
from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextSendMessage,
    TemplateSendMessage,
    ButtonsTemplate,
    MessageTemplateAction,
)
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
first = True
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
        # print("User!")
        self.items=[]
        self.getnewLocation = False

############ is_going ############
    def is_going_to_greeting(self, event):
        text = event.message.text
        return text.lower() == "hi"

    def is_going_to_showFSM(self, event):
        text = event.message.text
        return text.lower() == "fsm"

    # def is_going_to_state1(self, event):
    #     text = event.message.text
    #     return text.lower() == "go to state1"
    
    def is_going_to_eat(self, event):
        text = event.message.text
        return text.lower() == "吃東西"

    def is_going_to_drink(self, event):
        text = event.message.text
        return text.lower() == "喝飲料"
    def is_going_to_drink(self, event):
        text = event.message.text
        return text.lower() == "踩雷"

    def is_going_to_FindRestaurant(self, event):
        return self.ans == "吃東西"

    def is_going_to_FindDrink(self, event):
        return self.ans == "喝飲料"

    def is_going_to_FindBomb(self, event):
        return self.ans == "踩雷"

    def is_going_to_FindnewRestaurant(self, event):
        text = event.message.text
        print("FindnewRestaurant text: ",text)
        if(text == '換一間啦'):
            return True
        else:
            return False
    def is_going_to_FindnewDrink(self, event):
        text = event.message.text
        print("FindnewDrink text: ",text)
        if(text == '換一間啦'):
            return True
        else:
            return False
    def is_going_to_getLocation_again(self, event):
        text = event.message.text
        print("getLocation_again text: ",text)
        if("地點" or "地方" or "位置" in text):
            return True
        else:
            return False
    def is_going_to_greeting_again(self, event):
        text = event.message.text
        print("text: ",text)
        if('換一間啦' or "地點" or "地方" or "位置" in text):
            return False
        else:
            return True
############ on_enter ############
    def on_enter_greeting(self, event):
        print("I'm entering greeting")
        global first
        first = True
        reply_token = event.reply_token
        self.items.clear()
        # send_text_message(reply_token, "Trigger greeting")
        self.breakfastbutton = QuickReplyButton(
            action=PostbackAction(label="吃東西",data="吃東西", text = "吃東西")
        )
        self.items.append(self.breakfastbutton)
        self.lunchbutton = QuickReplyButton(
            action=PostbackAction(label="喝飲料",data="喝飲料", text = "喝飲料")
        )
        self.items.append(self.lunchbutton)
        self.randombutton = QuickReplyButton(
            action=PostbackAction(label="踩雷",data="踩雷", text = "踩雷")
        )
        self.items.append(self.randombutton)
        self.message = TextSendMessage(
            text="""
嗨囉~\n
我是機器人哲哥\n
我可以幫你決定要吃什麼喔！\n
你可以透過下面選單點選或是直接按快速回復按鈕來開始\n
讓你不再為了要吃什麼而煩惱~\n
            """,
            quick_reply=QuickReply(
                items=self.items
            
            ),
        )
        line_bot_api.reply_message(reply_token, self.message)
        # self.go_back()

    def on_enter_showFSM(self, event):
        reply_token = event.reply_token
        img_url = "https://i.imgur.com/E8jsNfR.png"
        try:
            message = ImageSendMessage(original_content_url=img_url, preview_image_url=img_url)
            line_bot_api.reply_message(reply_token,message)
        except:
            print("fail to get fsm")
        self.go_back()

    def on_enter_getLocation(self, event):
        self.ans = event.message.text
        if self.ans == "吃東西":
            self.mode = "eat"
        elif self.ans == "喝飲料":
            self.mode = "drink"
        print("ans: ", self.ans)
        if not first:
            self.getnewLocation = True
            if self.mode == "eat":
                self.ans = "吃東西"
            elif self.mode == "drink":
                self.ans = "喝飲料"
        print("new ans: ", self.ans)
        reply_token = event.reply_token
        send_text_message(reply_token, "請輸入你的位置")

    # def on_enter_state1(self, event):
    #     print("I'm entering state1")

    #     reply_token = event.reply_token
    #     # send_text_message(reply_token, "Trigger state1")
    #     sticker_message = StickerSendMessage(	
    #         package_id='446',	
    #         sticker_id='1988'	
    #     )	
    #     line_bot_api.reply_message(reply_token, sticker_message)
    #     self.go_back()

    def on_enter_FindRestaurant(self, event):
        self.mode = "eat"
        print("I'm entering FindRestaurant")
        # print("Res ans = ", self.ans)
        text = event.message.text
        global first
        if first:
            self.previous_address = text
            first = False
        if self.getnewLocation and "換一間啦" not in text:
            self.previous_address = text

        ### get lat and lng
        address = urllib.request.quote(self.previous_address)
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
        if self.ans == "吃東西":
            foodStoreSearch = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?key={}&location={},{}&rankby=distance&type=restaurant&language=zh-TW".format(Google_Map_API_KEY, lat, lng)
        elif self.ans == "喝飲料":
            foodStoreSearch = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?key={}&location={},{}&rankby=distance&keyword=飲料&language=zh-TW".format(Google_Map_API_KEY, lat, lng)
        else:
             foodStoreSearch = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?key={}&location={},{}&rankby=distance&language=zh-TW".format(Google_Map_API_KEY, lat, lng)
        foodReq = requests.get(foodStoreSearch)
        nearby_restaurants_dict = foodReq.json()
        top20_restaurants = nearby_restaurants_dict['results']
        res_num = len(top20_restaurants)
        bravo = []
        for i in range(res_num):
            try:
                if top20_restaurants[i]['rating'] > 4:
                    print('rate: ', top20_restaurants[i]['rating'])
                    bravo.append(i)
            except:
                KeyError
        if len(bravo) < 0:
            reply_token = event.reply_token
            send_text_message(reply_token, "你附近沒有雷!")
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
        details = "Google Map 評分: {}\n地址:{}".format(rating, address)
        print(details)

        map_url = "https://www.google.com/maps/search/?api=1&query={lat},{long}&query_place_id={place_id}".format(lat=restaurant["geometry"]["location"]["lat"], long=restaurant["geometry"]["location"]["lng"], place_id= restaurant["place_id"])
        ###
        print("Find Restaurant")
        print("title: ", restaurant['name'])
        ### reply
        reply_token = event.reply_token

        buttons_template_message = TemplateSendMessage(
            alt_text = restaurant["name"],
            template = ButtonsTemplate(
                thumbnail_image_url = thumbnail_image_url,
                title = restaurant['name'],
                text= details,
                actions=[
                    URITemplateAction(
                        label='查看地圖',
                        uri=map_url
                    ),
                    PostbackTemplateAction(
                        label='換一間啦',
                        text='換一間啦',
                        data='換一間啦'
                    )
                ]
            )
        )
        line_bot_api.reply_message(reply_token, buttons_template_message)
        # self.go_back_greeting()

    def on_enter_FindDrink(self, event):
        self.mode = "drink"
        print("I'm entering FindDrink")
        # print("Res ans = ", self.ans)
        text = event.message.text
        global first
        if first:
            self.previous_address = text
            first = False

        ### get lat and lng
        address = urllib.request.quote(self.previous_address)
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
        if self.ans == "吃東西":
            foodStoreSearch = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?key={}&location={},{}&rankby=distance&type=restaurant&language=zh-TW".format(Google_Map_API_KEY, lat, lng)
        elif self.ans == "喝飲料":
            foodStoreSearch = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?key={}&location={},{}&rankby=distance&keyword=飲料&language=zh-TW".format(Google_Map_API_KEY, lat, lng)
        else:
             foodStoreSearch = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?key={}&location={},{}&rankby=distance&language=zh-TW".format(Google_Map_API_KEY, lat, lng)
        foodReq = requests.get(foodStoreSearch)
        nearby_restaurants_dict = foodReq.json()
        top20_restaurants = nearby_restaurants_dict['results']
        res_num = len(top20_restaurants)
        bravo = []
        for i in range(res_num):
            try:
                if top20_restaurants[i]['rating'] > 4:
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
        details = "Google Map 評分: {}\n地址:{}".format(rating, address)
        print(details)

        map_url = "https://www.google.com/maps/search/?api=1&query={lat},{long}&query_place_id={place_id}".format(lat=restaurant["geometry"]["location"]["lat"], long=restaurant["geometry"]["location"]["lng"], place_id= restaurant["place_id"])
        ###
        print("Find Restaurant")
        print("title: ", restaurant['name'])
        ### reply
        reply_token = event.reply_token

        buttons_template_message = TemplateSendMessage(
            alt_text = restaurant["name"],
            template = ButtonsTemplate(
                thumbnail_image_url = thumbnail_image_url,
                title = restaurant['name'],
                text= details,
                actions=[
                    URITemplateAction(
                        label='查看地圖',
                        uri=map_url
                    ),
                    PostbackTemplateAction(
                        label='換一間啦',
                        text='換一間啦',
                        data='換一間啦'
                    )
                ]
            )
        )
        line_bot_api.reply_message(reply_token, buttons_template_message)

    def on_enter_FindBomb(self, event):
        self.mode = "bomb"
        print("I'm entering FindBomb")
        # print("Res ans = ", self.ans)
        text = event.message.text
        global first
        if first:
            self.previous_address = text
            first = False

        ### get lat and lng
        address = urllib.request.quote(self.previous_address)
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
        if self.ans == "吃東西":
            foodStoreSearch = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?key={}&location={},{}&rankby=distance&type=restaurant&language=zh-TW".format(Google_Map_API_KEY, lat, lng)
        elif self.ans == "喝飲料":
            foodStoreSearch = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?key={}&location={},{}&rankby=distance&keyword=飲料&language=zh-TW".format(Google_Map_API_KEY, lat, lng)
        else:
             foodStoreSearch = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?key={}&location={},{}&rankby=distance&language=zh-TW".format(Google_Map_API_KEY, lat, lng)
        foodReq = requests.get(foodStoreSearch)
        nearby_restaurants_dict = foodReq.json()
        top20_restaurants = nearby_restaurants_dict['results']
        res_num = len(top20_restaurants)
        bravo = []
        for i in range(res_num):
            try:
                if top20_restaurants[i]['rating'] <= 4:
                    print('rate: ', top20_restaurants[i]['rating'])
                    bravo.append(i)
            except:
                KeyError
        if len(bravo) < 0:
            send_text_message(reply_token, "你附近沒有雷!")
            self.go_back()
        
        restaurant = top20_restaurants[random.choice(bravo)]

        if restaurant.get("photos") is None:
            thumbnail_image_url = None
        else:
            photo_reference = restaurant["photos"][0]["photo_reference"]
            photo_width = restaurant["photos"][0]["width"]
            thumbnail_image_url = "https://maps.googleapis.com/maps/api/place/photo?key={}&photoreference={}&maxwidth={}".format(Google_Map_API_KEY, photo_reference, photo_width)
        
        rating = "無" if restaurant.get("rating") is None else restaurant["rating"]
        address = "沒有資料" if restaurant.get("vicinity") is None else restaurant["vicinity"]
        details = "Google Map 評分: {}\n地址:{}".format(rating, address)
        print(details)

        map_url = "https://www.google.com/maps/search/?api=1&query={lat},{long}&query_place_id={place_id}".format(lat=restaurant["geometry"]["location"]["lat"], long=restaurant["geometry"]["location"]["lng"], place_id= restaurant["place_id"])
        ###
        print("Find Restaurant")
        print("title: ", restaurant['name'])
        ### reply
        reply_token = event.reply_token

        buttons_template_message = TemplateSendMessage(
            alt_text = restaurant["name"],
            template = ButtonsTemplate(
                thumbnail_image_url = thumbnail_image_url,
                title = restaurant['name'],
                text= details,
                actions=[
                    URITemplateAction(
                        label='查看地圖',
                        uri=map_url
                    ),
                ]
            )
        )
        line_bot_api.reply_message(reply_token, buttons_template_message)
        self.go_back()
############ on_exit ############
    # def on_exit_state1(self):
    #     print("Leaving state1")
import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# Google Map API
import requests
import urllib.request
import json
import time

from fsm import TocMachine
from utils import send_text_message

load_dotenv()


machine = TocMachine(
    states=["user", "greeting","showFSM","getLocation","FindRestaurant","FindDrink","FindBomb"],
    transitions=[
        {
            "trigger": "advance",
            "source": "user",
            "dest": "greeting",
            "conditions": "is_going_to_greeting",
        },
        {
            "trigger": "advance",
            "source": "user",
            "dest": "showFSM",
            "conditions": "is_going_to_showFSM",
        },
        {
            "trigger": "advance",
            "source": "greeting",
            "dest": "getLocation",
            "conditions": "is_going_to_eat",
        },
        {
            "trigger": "advance",
            "source": "greeting",
            "dest": "getLocation",
            "conditions": "is_going_to_drink",
        },
        {
            "trigger": "advance",
            "source": "greeting",
            "dest": "getLocation",
            "conditions": "is_going_to_Bomb",
        },
        {
            "trigger": "advance",
            "source": "getLocation",
            "dest": "FindRestaurant",
            "conditions": "is_going_to_FindRestaurant",
        },
        {
            "trigger": "advance",
            "source": "getLocation",
            "dest": "FindDrink",
            "conditions": "is_going_to_FindDrink",
        },
        {
            "trigger": "advance",
            "source": "getLocation",
            "dest": "FindBomb",
            "conditions": "is_going_to_FindBomb",
        },
        {
            "trigger": "advance",
            "source": "FindRestaurant",
            "dest": "FindRestaurant",
            "conditions": "is_going_to_FindnewRestaurant",
        },
        {
            "trigger": "advance",
            "source": "FindDrink",
            "dest": "FindDrink",
            "conditions": "is_going_to_FindnewDrink",
        },
        {
            "trigger": "advance", 
            "source": ["FindRestaurant","FindDrink"],
            "dest": "getLocation",
            "conditions": "is_going_to_getLocation_again",
        },
        {
            "trigger": "advance", 
            "source": ["FindRestaurant","FindDrink"],
            "dest": "greeting",
            "conditions": "is_going_to_greeting_again",
        },
        {   "trigger": "go_back", 
            "source": ["showFSM","FindBomb"],
            "dest": "user"
        },
    ],
    initial="user",
    auto_transitions=False,
    show_conditions=True,
)

app = Flask(__name__, static_url_path="")


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


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.message.text)
        )

    return "OK"


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)
    # print("***********"+str(events)+"************\n")

    # if(events.message.type == "location"):
    #     print("location")
    #     print("latitude: "+ events.latitude)
    #     print("longitude: "+ events.longitude)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        # print("typeee: "+ str(event.message.type))
        if event.type == 'postback':
            # print("EEEE:", event.message.text)
            print("EEEE:")
        elif(event.message.type == "location"):
            print("location")
            print("latitude: "+ str(event.message.latitude))
            print("longitude: "+ str(event.message.longitude))
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f"\nFSM STATE: {machine.state}")
        print(f"REQUEST BODY: \n{body}")
        response = machine.advance(event)
        if response == False:
            send_text_message(event.reply_token, "Not Entering any State")

    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
    show_fsm()
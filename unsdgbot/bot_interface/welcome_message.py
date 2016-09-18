"""
    Creates the welcome message for our bot by sending a request to Facebook.

    Edit the message_json and run either:
        $ python welcome_message.py --action create
    OR
        $ python welcome_message.py --action delete
"""

import sys
import os.path
import argparse
import requests
import ConfigParser

# Append parent directory to python path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from config import Config

# Get some configs
config = ConfigParser.ConfigParser()
config.read("../local_test_config.cfg")

FB_MESSAGING_URL = (
    "https://graph.facebook.com"
    "/v{0}/me/thread_settings?access_token={1}"
).format(Config.FB_API_VERSION, config.get('SECRET', 'fb_access_token'))


def create_background_greeting_message():
    # only appears for new users
    message_json = {
        "setting_type": "greeting",
        "greeting": {
            "text": "Start chatting with me about the UN Sustainable Development Goals!"
        }
    }

    response = requests.post(FB_MESSAGING_URL,
                             json=message_json,
                             headers={"Content-Type": "application/json"})

    print(response.content)
    if response.status_code == 200:
        print('Success CREATE!!')
    else:
        raise Exception('Message update failed!')


def create_welcome_message():

    message_json = {
        "setting_type": "call_to_actions",
        "thread_state": "new_thread",
        "call_to_actions": [{
            "payload": "WELCOME_MESSAGE_POSTBACK"
        }]
    }

    response = requests.post(
        FB_MESSAGING_URL,
        json=message_json,
        headers={"Content-Type": "application/json"})

    print(response.content)
    if response.status_code == 200:
        print('Success CREATE!!')
    else:
        raise Exception('Message update failed!')


def delete_welcome_message():
    message_json = {
        "setting_type": "call_to_actions",
        "thread_state": "new_thread",
        "call_to_actions": []
    }

    response = requests.post(
        FB_MESSAGING_URL,
        json=message_json,
        headers={"Content-Type": "application/json"})

    print(response.content)
    if response.status_code == 200:
        print('Success DELETE!!')
    else:
        raise Exception('Message update failed!')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Change welcome message.')
    parser.add_argument('--action', type=str,
                        help="either delete create or background")

    args = parser.parse_args()
    if args.action == "delete":
        delete_welcome_message()
    elif args.action == "background":
        create_background_greeting_message()
    elif args.action == "create":
        create_welcome_message()
    else:
        print("No action was recognized...nothing was executed")

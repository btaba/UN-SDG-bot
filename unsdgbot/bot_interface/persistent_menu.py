"""
    Creates the persistent menu by sending a request to Facebook.

    Edit the message_json and run either:
        $ python persistent_menu.py --action create
    OR
        $ python persistent_men.py --action delete
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


def create_persistent_menu():
    message_json = {
        "setting_type": "call_to_actions",
        "thread_state": "existing_thread",
        "call_to_actions": [
            {
                "type": "postback",
                "title": "What are the SDGs?",
                "payload": "SDG_POSTBACK"
            },
            {
                "type": "postback",
                "title": "Latest News",
                "payload": "LATEST_POSTBACK"
            },
            {
                "type": "postback",
                "title": "Help",
                "payload": "HELP_POSTBACK"
            }
        ]
    }

    response = requests.post(
        FB_MESSAGING_URL,
        json=message_json,
        headers={"Content-Type": "application/json"}
    )

    print(response.content)
    if response.status_code == 200:
        print('Success CREATE!!')
    else:
        raise Exception('Message update failed!')


def delete_persistent_menu():

    message_json = {
        "setting_type": "call_to_actions",
        "thread_state": "existing_thread",
        "call_to_actions": []
    }

    response = requests.post(
        FB_MESSAGING_URL,
        json=message_json,
        headers={"Content-Type": "application/json"}
    )

    print(response.content)
    if response.status_code == 200:
        print('Success DELETE!!')
    else:
        raise Exception('Persistent menu update failed!')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Change persistent menu.')
    parser.add_argument('--action', type=str,
                        help="either delete or create")

    args = parser.parse_args()
    if args.action == "delete":
        delete_persistent_menu()
    else:
        create_persistent_menu()

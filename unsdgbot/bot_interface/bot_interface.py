"""
    Interface to communicate with Facebook Messenger
    https://developers.facebook.com/docs/messenger-platform/send-api-reference
"""

import json
import requests
import warnings

from enum import Enum


class NotificationType(Enum):
    REGULAR = "REGULAR"
    SILENT_PUSH = "SILENT_PUSH"
    NO_PUSH = "NO_PUSH"


class RecipientMethod(Enum):
    ID = "id"
    PHONE_NUMBER = "phone_number"


class AttachmentType(Enum):
    IMAGE = "image"
    TEMPLATE = "template"
    BUTTON = "button"


class ButtonType(Enum):
    WEBURL = "web_url"
    POSTBACK = "postback"
    SHARE = "element_share"


class SenderActions(Enum):
    SEEN = "mark_seen"
    TYPING_ON = "typing_on"
    TYPING_OFF = "typing_off"


class BotInterface(object):
    def __init__(self, fb_api_version, fb_access_token):
        self.FB_API_VERSION = fb_api_version
        self.FB_ACCESS_TOKEN = fb_access_token

        self.URL = (
            "https://graph.facebook.com"
            "/v{0}/me/messages?access_token={1}"
        ).format(self.FB_API_VERSION, self.FB_ACCESS_TOKEN)

    def create_text_message(self, recipient_info, message,
                            recipient_method=RecipientMethod.ID.value,
                            notification_type=NotificationType.REGULAR.value):

        recipient_json = {recipient_method: recipient_info}

        message = {
            "recipient": recipient_json,
            "message": {
                "text": message
            },
            "notification_type": notification_type
        }

        return message

    def create_generic_payload_message(self, recipient_info,
                                       recipient_method=RecipientMethod.ID.value,
                                       notification_type=NotificationType.REGULAR.value,
                                       attachment={}):
        message = self.create_text_message(recipient_info, None,
                                           recipient_method, notification_type)

        message["message"] = {"attachment": attachment}

        return message

    def add_quick_replies(self, message_json, quick_replies=[]):
        message_json["message"]["quick_replies"] = quick_replies
        return message_json

    #################### CREATE TEMPLATES ####################

    def create_generic_template(self, template_elements=[]):
        """
            template_elements: Array of generic_template_elements
        """
        assert type(template_elements) == list

        attachment = {
            "type": AttachmentType.TEMPLATE.value,
            "payload": {
                "template_type": "generic",
                "elements": template_elements
            }
        }
        return attachment

    def create_image_template(self, image_url=""):
        """
            image_url: this should be the image URL
        """
        assert type(image_url) == str

        attachment = {
            "type": AttachmentType.IMAGE.value,
            "payload": {
                "url": image_url,
            }
        }
        return attachment

    def create_button_template(self, button_title="", buttons=[]):
        assert type(button_title) in [str, unicode]
        assert type(buttons) == list
        assert len(buttons) > 0

        attachment = {
            "type": AttachmentType.TEMPLATE.value,
            "payload": {
                "template_type": "button",
                "text": button_title,
                "buttons": buttons
            }
        }

        return attachment

    #################### CREATE ELEMENTS/BUTTONS ####################

    def create_generic_template_element(self, element_title="", element_item_url="",
                                        element_image_url="", element_subtitle="",
                                        element_buttons=None):
        """
            element_title:      Some title
            element_item_url:   URL opened when button is tapped
            element_image_url:  Bubble Image
            element_subtitle:   Bubble subtitle
            element_buttons:    Array of buttons
        """
        element = {
            "title": element_title,
            "item_url": element_item_url,
            "image_url": element_image_url,
            "subtitle": element_subtitle
        }

        if element_buttons:
            assert type(element_buttons) == list
            element['buttons'] = element_buttons

        return element

    def create_button(self, button_type=ButtonType.WEBURL.value,
                      title="", url="", payload=""):
        assert type(title) in [str, unicode]
        assert type(url) == str
        assert type(payload) == str

        button_dict = {}
        if button_type == ButtonType.WEBURL.value:
            assert len(url) > 0
            button_dict = {
                "type": ButtonType.WEBURL.value,
                "title": title,
                "url": url
            }
            return button_dict
        elif button_type == ButtonType.POSTBACK.value:
            assert len(payload) > 0
            button_dict = {
                "type": ButtonType.POSTBACK.value,
                "title": title,
                "payload": payload
            }
            return button_dict
        elif button_type == ButtonType.SHARE.value:
            button_dict = {
                "type": ButtonType.SHARE.value
            }

        warnings.warn("button_type of %s does not exist" % button_type, UserWarning)
        return button_dict

    def create_quick_reply(self, title="", payload="", image_url=""):
        quick_reply = {
            "content_type": "text",
            "title": title,
            "payload": payload
        }

        if len(image_url) > 0:
            quick_reply["image_url"] = image_url

        return quick_reply


    #################### SEND MESSAGE FUNCTIONS ####################

    def send_text_message(self, recipient_info, message,
                          recipient_method=RecipientMethod.ID.value,
                          notification_type=NotificationType.REGULAR.value):

        message = self.create_text_message(recipient_info, message,
                                           recipient_method, notification_type)

        return self._send(message)

    def send_sender_action(self, recipient_info, sender_action=SenderActions.SEEN.value):
        message = {"recipient": {"id": recipient_info}, "sender_action": sender_action}
        return self._send(message)

    def send_generic_payload_message(self, recipient_info,
                                     recipient_method=RecipientMethod.ID.value,
                                     notification_type=NotificationType.REGULAR.value,
                                     elements=[]):

        attachment = self.create_generic_template(elements)

        message = self.create_generic_payload_message(recipient_info,
                                                      recipient_method, notification_type,
                                                      attachment=attachment)

        return self._send(message)

    def send_image_payload_message(self, recipient_info,
                                   recipient_method=RecipientMethod.ID.value,
                                   notification_type=NotificationType.REGULAR.value,
                                   image_url=""):

        attachment = self.create_image_template(image_url)

        message = self.create_generic_payload_message(recipient_info,
                                                      recipient_method, notification_type,
                                                      attachment=attachment)

        return self._send(message)

    def send_button_payload_message(self, recipient_info,
                                    recipient_method=RecipientMethod.ID.value,
                                    notification_type=NotificationType.REGULAR.value,
                                    button_title="", buttons=[]):

        attachment = self.create_button_template(button_title, buttons)

        message = self.create_generic_payload_message(recipient_info,
                                                      recipient_method, notification_type,
                                                      attachment=attachment)

        return self._send(message)

    def _send(self, message_json):
        response = requests.post(self.URL, json=message_json,
                                 headers={"Content-Type": "application/json"})

        if response.status_code != 200:
            raise Exception("The Facebook API did not like the message we tried to send them",
                            response.content)

        return response

    def get_user_profile_info(self, user_id):
        url = (
            "https://graph.facebook.com"
            "/v{0}/{1}?fields=first_name,last_name,profile_pic,locale,timezone,gender&access_token={2}"
        ).format(self.FB_API_VERSION, user_id, self.FB_ACCESS_TOKEN)

        response = requests.get(url, headers={"Content-Type": "application/json"})

        return json.loads(response.content)

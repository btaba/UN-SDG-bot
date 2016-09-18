"""
    Tests for the Facebook Messenger Bot Interface

    Run in directory with local config files
    > nosetests

"""

import unittest
import ConfigParser

from config import Config
from bot_interface.bot_interface import *

config = ConfigParser.ConfigParser()
config.read("local_test_config.cfg")


class TestBotInterface(unittest.TestCase):

    def testBotInterfaceInit(self):
        bot = BotInterface(Config.FB_API_VERSION, config.get('SECRET', 'fb_access_token'))
        self.assertIsNotNone(bot)

    def testSendTextMessage(self):
        bot = BotInterface(Config.FB_API_VERSION, config.get('SECRET', 'fb_access_token'))
        response = bot.send_text_message(config.get('SECRET', 'fb_test_recipient_id'),
            'Testing the bot interface testSendTextMessage', RecipientMethod.ID.value,
            NotificationType.REGULAR.value)
        print(response)

        self.assertEqual(response.status_code, 200)

    def testSendPayloadMessageImage(self):
        bot = BotInterface(Config.FB_API_VERSION, config.get('SECRET', 'fb_access_token'))
        response = bot.send_image_payload_message(config.get('SECRET', 'fb_test_recipient_id'),
            RecipientMethod.ID.value, NotificationType.REGULAR.value,
            image_url="https://media-cdn.tripadvisor.com/media/photo-s/04/17/78/62/peruvian-andes-adventures.jpg")
        print(response)
        self.assertEqual(response.status_code, 200)

    def testSendPayloadMessageGeneric(self):
        bot = BotInterface(Config.FB_API_VERSION, config.get('SECRET', 'fb_access_token'))

        elements = []

        button = bot.create_button(button_type=ButtonType.WEBURL.value,
            title="Test Button", url="http://www.nytimes.com/")
        elements.append(bot.create_generic_template_element(element_title="Test Title 1", element_item_url="http://www.nytimes.com/",
            element_image_url="https://media-cdn.tripadvisor.com/media/photo-s/04/17/78/62/peruvian-andes-adventures.jpg",
            element_subtitle="the andes are so beautiful!!", element_buttons=[button]))

        elements.append(bot.create_generic_template_element(element_title="Test Title 2", element_item_url="http://www.google.com/",
            element_image_url="https://media-cdn.tripadvisor.com/media/photo-s/04/17/78/62/peruvian-andes-adventures.jpg",
            element_subtitle="I would really like to go there."))

        response = bot.send_generic_payload_message(config.get('SECRET', 'fb_test_recipient_id'),
            RecipientMethod.ID.value, NotificationType.REGULAR.value,
            elements=elements)

        self.assertEqual(response.status_code, 200)

    def testSendPayloadMessageButton(self):
        bot = BotInterface(Config.FB_API_VERSION, config.get('SECRET', 'fb_access_token'))

        # URL button
        buttons = []
        buttons.append(bot.create_button(button_type=ButtonType.WEBURL.value,
            title="Test Button", url="http://www.nytimes.com/"))
        buttons.append(bot.create_button(button_type=ButtonType.WEBURL.value,
            title="Test Button 2", url="http://www.nytimes.com/"))
        response = bot.send_button_payload_message(config.get('SECRET', 'fb_test_recipient_id'),
            RecipientMethod.ID.value, NotificationType.REGULAR.value,
            button_title="Test Button Title", buttons=buttons)
        self.assertEqual(response.status_code, 200)

        # Callback button
        buttons = []
        buttons.append(bot.create_button(button_type=ButtonType.POSTBACK.value,
            title="Test Button", payload='USER_DEFINED_PAYLOAD_FOR_THIS_BUTTON'))
        response = bot.send_button_payload_message(config.get('SECRET', 'fb_test_recipient_id'),
            RecipientMethod.ID.value, NotificationType.REGULAR.value,
            button_title="Test Button Title", buttons=buttons)
        self.assertEqual(response.status_code, 200)

    def testGetUserProfileInfo(self):
        bot = BotInterface(Config.FB_API_VERSION, config.get('SECRET', 'fb_access_token'))

        response = bot.get_user_profile_info(config.get('SECRET', 'fb_test_recipient_id'))

        self.assertIs(type(response), dict)
        self.assertIn("first_name", response.keys())
        self.assertIn("profile_pic", response.keys())

    def testSenderAction(self):
        bot = BotInterface(Config.FB_API_VERSION, config.get('SECRET', 'fb_access_token'))

        response = bot.send_sender_action(config.get('SECRET', 'fb_test_recipient_id'),
                                          SenderActions.TYPING_ON.value)
        self.assertEqual(response.status_code, 200)

"""
    Message processor - the heart of our robot

    Parse messages from Facebook:
        https://developers.facebook.com/docs/messenger-platform/webhook-reference

"""

import time
import random
import pickle
import bot_response_text
# from textblob import TextBlob

from SDGs import goals
from sdg_suggester import SDGSuggester
from bot_interface.bot_interface import ButtonType, SenderActions


class FacebookMessage(object):
    def __init__(self, m):
        self.timestamp = m['timestamp']
        message = m['message']

        self.message_id = message['mid']
        self.message_seq_num = message['seq']

        if message.get('text'):
            self.message_text = message['text']
        else:
            self.message_text = None

        if message.get('attachments'):
            self.message_attachments = message['attachments']
            if message.get('sticker_id'):
                self.message_sticker_id = message['sticker_id']
            else:
                self.message_sticker_id = None
        else:
            self.message_attachments = None
            self.message_sticker_id = None

        if message.get('quick_reply'):
            self.quick_reply_payload = message['quick_reply']['payload']
        else:
            self.quick_reply_payload = None


class Parser(object):

    def __init__(self, bot, nyt):
        self.BOT = bot
        self.NYT_API = nyt

    def send_trending_articles(self, recipient_id):
        #call return_trending_list function for intent = latest
        nyt_response = self.NYT_API.return_trending_list()
        template_elements = self.make_nyt_response_templates(nyt_response)
        if len(template_elements) > 0:
            response = self.BOT.send_text_message(
                recipient_id,
                "Here's the latest in sustainability from the NY Times:")
            response = self.BOT.send_generic_payload_message(
                recipient_id,
                elements=template_elements)
            return response

        # no trending articles were returned!
        response = self.BOT.send_text_message(recipient_id, u"Sorry, couldn't find anything trending in climate change today. Please check back tomorrow! \U0001f30e")
        return response

    def make_nyt_response_templates(self, nyt_response):
        template_elements = []
        for nyt in nyt_response:
            if nyt.get("image_url"):
                nyt_image_url = nyt["image_url"]
            else:
                nyt_image_url = None

            if nyt["abstract"] is None:
                # Facebook requires that the subtitle is not None
                nyt["abstract"] = nyt["title"]

            share_button = self.BOT.create_button(button_type=ButtonType.SHARE.value)
            read_button = self.BOT.create_button(button_type=ButtonType.WEBURL.value,
                title="Read", url=str(nyt["web_url"]))
            template_elements.append(
                self.BOT.create_generic_template_element(
                    element_title=nyt["title"], element_item_url=nyt["web_url"],
                    element_image_url=nyt_image_url, element_subtitle=nyt["abstract"],
                    element_buttons=[read_button, share_button]
                )
            )

        return template_elements

    def send_cannot_compute_helper_callback(self, recipient_id):

        response = self.BOT.send_text_message(recipient_id, bot_response_text.help_text)

        return response

    def send_welcome_message(self, recipient_id):
        """
            Sends the user different welcome messages depending on whether
                they exist in our database or not
        """

        welcome_message = self.BOT.create_generic_payload_message(
            recipient_id,
            attachment=bot_response_text.welcome_message[0])
        response = self.BOT._send(welcome_message)

        # The rest of the welcome_messages are plain text
        for j in xrange(1, len(bot_response_text.welcome_message)):
            response = self.BOT.send_text_message(
                recipient_id,
                bot_response_text.welcome_message[j]
            )

        return response

    def send_sdg_generic_template(self, recipient_id, sdg_goals, sequence_id):
        share_button = self.BOT.create_button(button_type=ButtonType.SHARE.value)
        sdg_template_elements = []
        for sdg in sdg_goals:
            sdg_template_element = self.BOT.create_generic_template_element(
                element_title=str(sdg["goal"]) + ". " + sdg["short"], element_item_url=sdg["url"],
                element_image_url=sdg["image_url"], element_subtitle=sdg["title"],
                element_buttons=[share_button]
            )
            sdg_template_elements.append(
                sdg_template_element
            )

        attachment = self.BOT.create_generic_template(sdg_template_elements)
        message = self.BOT.create_generic_payload_message(recipient_id, attachment=attachment)

        if sequence_id < 3:
            message = self.BOT.add_quick_replies(
                message,
                bot_response_text.get_sdg_quick_replies(sequence_id + 1)
            )

        response = self.BOT._send(message)

        return response

    def send_sdg_explanation(self, recipient_id, sequence_id=1):
        if sequence_id == 1:

            # send intro
            sdg_intro = self.BOT.create_text_message(
                recipient_id,
                message=bot_response_text.sdg_intro)
            response = self.BOT._send(sdg_intro)

            # send sdg_goals
            sdg_goals = goals.sdg_goals["goals"][0:5]

        elif sequence_id == 2:
            sdg_goals = goals.sdg_goals["goals"][5:10]

        elif sequence_id == 3:
            sdg_goals = goals.sdg_goals["goals"][10:]

        else:
            raise Exception('SDG sequence id of %d does not exist' % sequence_id)

        response = self.send_sdg_generic_template(recipient_id, sdg_goals, sequence_id)

        if sequence_id == 3:
            end_message = self.BOT.create_text_message(
                recipient_id,
                message="That's all folks!")
            response = self.BOT._send(end_message)

        return response


class MessageProcessor(object):
    """
        Processes incoming messages from Facebook and directs functionaility
            to WitParser or other parsing objects that send responses back to the user
    """

    def __init__(self, bot, parser, config):
        self.BOT = bot
        self.CONFIG = config
        self.SDGSuggester = SDGSuggester()
        self.PARSER = parser
        self.cache_message_ids = []

    def parse_messages(self, messages):
        """
            Parses messages from Facebook as they come in, and chooses which actions
            to execute depending on the message type


            :rtype: response from requests.post() method
        """
        if self.CONFIG['DEBUG']:
            print(messages)

        # this is a really simple caching scheme, we should probably fix it later
        if len(self.cache_message_ids) > 200:
            self.cache_message_ids = self.cache_message_ids[-100:]

        for entry in messages['entry']:
            for m in entry['messaging']:
                response = None
                recipient_id = m['sender']['id']

                if m.get('message'):
                    """
                        Either an attachment or a text message will be parsed here
                            and sent to the Wit Processor, which will send a response
                            to the user
                    """

                    message = FacebookMessage(m)

                    if message.message_id in self.cache_message_ids:
                        continue

                    self.cache_message_ids.append(message.message_id)

                    if message.quick_reply_payload:
                        response = self.quick_reply_parser(recipient_id, message.quick_reply_payload)
                    elif message.message_text:
                        self.BOT.send_sender_action(recipient_id, SenderActions.TYPING_ON.value)

                        response_array = self.SDGSuggester.process_message(message.message_text)
                        if len(response_array) > 0:
                            for ra in response_array:
                                response = self.BOT.send_text_message(recipient_id, ra)
                        else:
                            response = self.BOT.send_text_message(recipient_id, bot_response_text.help_text)

                        self.BOT.send_sender_action(recipient_id, SenderActions.TYPING_OFF.value)

                    elif message.message_attachments:
                        self.BOT.send_sender_action(recipient_id, SenderActions.TYPING_ON.value)
                        # Parse and send back image
                        response = self.parse_and_respond_to_image_attachment(recipient_id, message)
                        self.BOT.send_sender_action(recipient_id, SenderActions.TYPING_OFF.value)

                elif m.get('postback'):
                    """
                        Someone clicks on a postback message we sent
                    """

                    postback_payload = m['postback']['payload']
                    if self.CONFIG['DEBUG']:
                        print('got postback %s' % postback_payload)

                    response = self.postback_parser(recipient_id, postback_payload)

            if response:
                return response

    def postback_parser(self, recipient_id, postback_payload):
        response = None

        if postback_payload == "HELP_POSTBACK":
            for help_text in bot_response_text.help_postback_text:
                response = self.BOT.send_text_message(recipient_id, help_text)
        elif postback_payload == "WELCOME_MESSAGE_POSTBACK":
            response = self.PARSER.send_welcome_message(recipient_id)
        elif postback_payload == "SDG_POSTBACK":
            response = self.PARSER.send_sdg_explanation(recipient_id)
        elif postback_payload == "LATEST_POSTBACK":
            response = self.PARSER.send_trending_articles(recipient_id)

        return response

    def quick_reply_parser(self, recipient_id, payload):
        if payload == "SDG_QUICK_REPLY_QUIT":
            response = self.BOT.send_text_message(
                recipient_id,
                "Ok, check them out later!"
            )
        elif payload == "SDG_QUICK_REPLY_CONTINUE2":
            response = self.PARSER.send_sdg_explanation(recipient_id, 2)
        elif payload == "SDG_QUICK_REPLY_CONTINUE3":
            response = self.PARSER.send_sdg_explanation(recipient_id, 3)
        return response

    def parse_and_respond_to_image_attachment(self, recipient_id, message):
        response = self.BOT.send_text_message(
            recipient_id,
            u'\U0001F44D'
        )
        return response

    def get_rand_int(self, max_int):
        return random.randint(0, max_int)

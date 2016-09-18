"""
    Some generic text that the bot will return

"""


def get_sdg_quick_replies(sequence_number=1):
    sdg_quick_replies = [
        {
            "content_type": "text",
            "title": 'Continue',
            "payload": 'SDG_QUICK_REPLY_CONTINUE' + str(sequence_number)
        },
        {
            "content_type": "text",
            "title": 'Quit',
            "payload": 'SDG_QUICK_REPLY_QUIT'
        }
    ]
    return sdg_quick_replies

help_text = u"I didn't find any suggestions in my database. Please check out the SDGs in the Menu. \U0001f30e"

help_postback_text = [
    (
        u"I can help inform you about the UN Sustainable Development Goals (SDGs)."
        u" Check out my Menu for Latest articles on sustainability or to read more about the SDGs.\n"
    ),
    (
        u"You can also type keywords or sentences about activities you do, and I'll help suggest simple ways "
        u"you can contribute to the SDGs!"
    )
]

sdg_intro = "SDGs are the Sustainable Development Goals set by the United Nations. Click around to learn more!"


welcome_message = [
    {
        "type": "template",
        "payload": {
            "template_type": "generic",
            "elements": [
                {
                    "title": "Welcome to the UN Sustainable Development Goals bot!",
                    "item_url": "https://www.facebook.com/climatechangebot/",
                    "image_url": "",
                    "subtitle": "I'll help you understand the Sustainable Development Goals!",
                }
            ]
        }
    },
    (
        u"Hey there! Use the menu bar to learn about the Sustainable Development Goals."
    ),
    u"You can also type a word and I can tell you how you can incorporate the SDGs into your daily life."
]

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

# help_button_title = [
#     (
#         u"Sorry I'm too busy worrying about climate change \U0001f30e, "
#         u"I missed what you were saying. If you need help worrying about"
#         u" climate change too, type 'help'."
#     ),
#     (
#         u"Sorry didn't catch that! \U0001f601 Type 'help', or search for something like"
#         u" 'crabs' or 'polar bears'!"
#     ),
#     (
#         u"Sorry didn't get that! \U0001f616 Type 'help', or search for something like"
#         u" 'sea levels' or 'melting glaciers'!"
#     )
# ]


# help_postback_text = [
#     (
#         u"I'm still learning, but what I can do now is: \n \u2022 Search for an article "
#         u"when you type something like 'show me articles about fish'. I can also search on keywords "
#         u"like if you type 'ice caps' \n"
#     ),
#     (
#         u"\u2022 Have a simple conversation with you; for example ask me: 'what is my name?' \n"
#         u"\u2022 I can give you the latest scoop on climate change, just type 'trending' or 'latest' \n"
#         u"That's all folks! \U0001f389"
#     )
# ]

sdg_intro = "SDGs are the Sustainable Development Goals set by the United Nations. Click to learn more!"


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

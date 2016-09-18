#!/usr/bin/env python
import logging

from flask import Flask, request
from flask import jsonify
from logging.handlers import RotatingFileHandler

# from rivescript import RiveScript
from bot_interface.bot_interface import BotInterface
from message_processor.message_processor import MessageProcessor, Parser
from nyt_interface.nyt_interface import NytimesApi

app = Flask(__name__)

app.config.from_object("config.DevelopmentConfig")
app.config.from_pyfile("local.cfg")

bot = BotInterface(app.config['FB_API_VERSION'], app.config['FB_ACCESS_TOKEN'])
nyt_api = NytimesApi(app.config['NYT_KEY'])
parser = Parser(bot, nyt_api)
msgproc = MessageProcessor(bot, parser, app.config)


@app.route("/webhook/" + app.config['FB_WEBHOOK_URL'], methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if (request.args.get("hub.verify_token") == app.config['FB_VERIFY_TOKEN']):
            return request.args.get("hub.challenge")
        else:
            return not_found(404)

    if request.method == 'POST':
        messages = request.json
        print messages
        response = msgproc.parse_messages(messages)
        print('Sent a message')
        print(response)

        return success(200)


@app.errorhandler(404)
def not_found(error):
    app.logger.error('Not found: %s', str(error))
    return jsonify(response={'success': False},
                   status=404,
                   message="Not Found"), 404


if not app.config['DEBUG']:
    @app.errorhandler(Exception)
    def unhandled_exception(e):
        # logs any unhandled errors in our code, and returns 500
        app.logger.error('Unhandled Exception: %s', (e))
        return jsonify(response={'success': False},
                       status=500,
                       message="Internal Server Error"), 500


def success(status=200, message=''):
    return jsonify(response={'success': True},
                   status=status,
                   mimetype="application/json",
                   message=message), 200


if __name__ == "__main__":
    # Flask error logger
    handler = RotatingFileHandler(app.config['LOGGING_DIRECTORY'], maxBytes=10000, backupCount=1)
    handler.setLevel(app.config['LOGGING_LEVEL'])
    formatter = logging.Formatter(app.config['LOGGING_FORMAT'])
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    # Run app
    app.run(host='0.0.0.0', port=80, debug=True)

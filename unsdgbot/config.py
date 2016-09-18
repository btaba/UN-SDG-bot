import os
import logging

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True

    FB_API_VERSION = 2.7
    FB_ACCESS_TOKEN = 'this-is-in-local-config'
    FB_VERIFY_TOKEN = 'this-is-in-local-config'
    FB_WEBHOOK_URL = 'this-is-in-local-config'

    LOGGING_FORMAT = (
        '%(asctime)s - %(name)s - %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    )
    LOGGING_DIRECTORY = '../logs/app.log'
    LOGGING_LEVEL = logging.ERROR


class ProductionConfig(Config):
    DEVELOPMENT = False
    DEBUG = False


class DevelopmentConfig(Config):
    # ngrok http -host-header=rewrite 192.168.33.11:80
    DEVELOPMENT = True
    DEBUG = True

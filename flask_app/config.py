from datetime import timedelta
from os import environ


class Config(object):
    """
    Base Configuration class used by to hold common configuration values.
    """
    DEBUG = True
    SECRET_KEY = 'EXAMPLE_SECRET_KEY'
    JWT_AUTH_URL_RULE = '/login'
    JWT_EXPIRATION_DELTA = timedelta(seconds=86400)
    USER_ENABLE_EMAIL = False
    USER_ENABLE_USERNAME = True
    OWM_API_KEY = "eca10491c6108a5448898a877d1fa6ad"

class LocalConfig(Config):
    """
    Configuration values used by default if you run the application using`python run_server.py`
    """
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///sqlite.db'


class TestConfig(Config):
    """
    Configuration values used by default if you run the application using`python run_server.py`
    """

    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_sqlite.db'

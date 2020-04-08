import os

class BaseConfig:
    DEBUG=False
    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))


class DevelopmentConfig(BaseConfig):
    ENV='development'
    DEBUG = True

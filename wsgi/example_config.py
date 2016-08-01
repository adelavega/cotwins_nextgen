import os

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'enter key here'

class ProductionConfig(Config):
    DEBUG = False

    SQLALCHEMY_DATABASE_URI = "??"

class StagingConfig(Config):
    DEVELOPMENT = False
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = "??"

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    EXP_DEBUG = False

    SQLALCHEMY_DATABASE_URI = "??"

    RESEARCH_DB_HOST = "??" # e.g. localhost on dev server
    RESEARCH_DB_USER = "??"
    RESEARCH_DB_PASSWORD = "??"
    RESEARCH_DB_NAME = "??"

class HomeConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = "postgresql://localhost/gfg_dev"

class OpenShift(Config):
    DEVELOPMENT = False
    DEBUG = False

    try:
        SQLALCHEMY_DATABASE_URI = os.environ['OPENSHIFT_POSTGRESQL_DB_URL']
    except:
        pass

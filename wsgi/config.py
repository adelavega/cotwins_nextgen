import os

class Config(object):
    DEBUG = False
    DEVELOPMENT = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = '\xc8U;\xe2w\xb3[c-:\xceeKu\xc9f\xd2\xaac\xfb\x1dZ\xc2\xc2'
    EXP_DEBUG = False

    try:
        SQLALCHEMY_DATABASE_URI = os.environ['OPENSHIFT_POSTGRESQL_DB_URL']
    except:
        SQLALCHEMY_DATABASE_URI = 'postgres://localhost/assesment'

class ProductionConfig(Config):
    pass

class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    EXP_DEBUG = True





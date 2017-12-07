import os

class Config(object):
    DEBUG = False
    DEVELOPMENT = False
    TESTING = False
    CSRF_ENABLED = True
    EXP_DEBUG = False

    try:
        SQLALCHEMY_DATABASE_URI = os.environ['POSTGRESQL_SERVICE_HOST']
    except:
        SQLALCHEMY_DATABASE_URI = 'postgres://localhost/assesment'

class ProductionConfig(Config):
    pass

class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = False

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    EXP_DEBUG = True





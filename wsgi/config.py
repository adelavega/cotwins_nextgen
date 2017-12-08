import os

class Config(object):
    DEBUG = False
    DEVELOPMENT = False
    TESTING = False
    CSRF_ENABLED = True
    EXP_DEBUG = False

    try:
        user = os.environ['DATABASE_USER']
        password = os.environ['DATABASE_PASSWORD']
        host = os.environ['DATA_SERVICE_HOST']
        port = os.environ['DATA_SERVICE_PORT']
        database = os.environ['DATABASE_NAME']
        SQLALCHEMY_DATABASE_URI = 'postgres://{}:{}@{}:{}/{}'.format(user, password, host, port, database)
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

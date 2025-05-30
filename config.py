import os

class DevelopmentConfig:
    SQLALCHEMY_DATBASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True

class TestingConfig:
    pass

class ProductionConfig:
    pass

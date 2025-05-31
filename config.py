import os

class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///mechanic_shop.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    CACHE_TYPE = 'SimpleCache'  
    CACHE_DEFAULT_TIMEOUT = '300'  # 5 minutes

class TestingConfig:
    pass

class ProductionConfig:
    pass

import os

class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///mechanic_shop.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    CACHE_TYPE = 'SimpleCache'  
    CACHE_DEFAULT_TIMEOUT = '300'  # 5 minutes

class TestingConfig:
   SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.db'
   debug = True 
   CACHE_TYPE = 'SimpleCache'

class ProductionConfig:
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///mechanic_shop.db'
    CACHE_TYPE = 'SimpleCache'


from asyncio.log import logger
from dotenv import load_dotenv
from pathlib import Path
import os

basedir = os.path.abspath(Path(__file__).parents[2])
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    HASHIDS_MIN_LENGTH : str | None = os.environ.get('HASHIDS_MIN_LENGTH', '8')
    HASHIDS_ALPHABET : str | None = os.environ.get('HASHIDS_ALPHABET', 'abcdefghijklmnopqrstuvwxyz1234567890')
    HASHIDS_SALT : str | None = os.environ.get('HASHIDS_SALT', 'gestion_universidad_salt')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    CACHE_REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    CACHE_REDIS_DB = int(os.getenv("REDIS_DB", 0))
    CACHE_REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
    CACHE_DEFAULT_TIMEOUT = 300

    @staticmethod
    def init_app(app) -> None:
        pass

class TestConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
class DevelopmentConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI')
        
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_RECORD_QUERIES = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_DATABASE_URI')
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

def factory(app: str) -> Config:
    configuration = {
        'testing': TestConfig,
        'development': DevelopmentConfig,
        'production': ProductionConfig
    }
    
    return configuration[app]
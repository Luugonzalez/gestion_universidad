import logging
from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from app.config import config
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_caching import Cache
from redis import Redis
import pickle 

db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
cache = Cache()

redis_client = None 

def create_app() -> Flask:
    """
    Using an Application Factory
    Ref: Book Flask Web Development Page 78
    """
    app_context = os.getenv('FLASK_CONTEXT')
    #https://flask.palletsprojects.com/en/stable/api/#flask.Flask
    app = Flask(__name__)
    f = config.factory(app_context if app_context else 'development')
    app.config.from_object(f)
  

    
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    cache.init_app(app)
    global redis_client
    redis_client = Redis(
            host=app.config['CACHE_REDIS_HOST'],
            port=app.config['CACHE_REDIS_PORT'],
            db=app.config['CACHE_REDIS_DB'],
            password=app.config['CACHE_REDIS_PASSWORD'],
            decode_responses=False  # importante para pickle
        )
    from app.resources import home, universidad_bp, facultad_bp, especialidad_bp
    
    app.register_blueprint(home, url_prefix="/api/v1")
    app.register_blueprint(universidad_bp, url_prefix="/api/v1")
    app.register_blueprint(facultad_bp, url_prefix="/api/v1")
    app.register_blueprint(especialidad_bp, url_prefix="/api/v1")


    @app.shell_context_processor    
    def ctx():
        return {"app": app}
    
    return app

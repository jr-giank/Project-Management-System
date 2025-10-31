from flask import Flask
from flasgger import Swagger

from config import Config
from .extensions import db, migrate
from .routes import register_routes

def app_init(config_object=Config):

    # Config
    app = Flask(__name__)
    app.config.from_object(config_object)
    db.init_app(app)

    if config_object != Config:
        migrate.init_app(app, db)

    app.config['SWAGGER'] = {
        "title": "Project Management API",
        "uiversion": 3
    }
    Swagger(app)

    # Models
    from app import models

    # Routes
    register_routes(app)

    return app
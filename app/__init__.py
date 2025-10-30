from flask import Flask
from flasgger import Swagger

from config import Config
from .extensions import db, migrate
from .routes import register_routes

def app_init():

    # Config
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)
    app.config['SWAGGER'] = {
        "title": "Project Management API",
        "uiversion": 3
    }
    Swagger(app)

    # Models
    from app.models import users

    # Routes
    register_routes(app)

    return app
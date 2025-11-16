from flask import Flask, jsonify
from flasgger import Swagger

from config import Config
from .extensions import db, migrate
from .routes import register_routes
from .seeders import user_seeder

def error_handlers(app):
    @app.errorhandler(Exception)
    def handle_errors(e):
        return jsonify({"error": str(e)}), 500

def app_init(config_object=Config):

    # Config
    app = Flask(__name__)
    app.config.from_object(config_object)
    db.init_app(app)

    migrate.init_app(app, db)
    error_handlers(app)

    @app.cli.command("seed")
    def seed():
        user_seeder.seed_users()

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
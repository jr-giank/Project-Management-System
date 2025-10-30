

from .users import users_bp
from .projects import projects_bp

def register_routes(app):

    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(projects_bp, url_prefix="/api/projects")
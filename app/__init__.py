from flask import Flask
from .routes import routes


def create_app():
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 3 * 1024 * 1024  # 3MB max file size
    # Registrar blueprint
    app.register_blueprint(routes)
    return app

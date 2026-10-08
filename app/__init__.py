import os
from flask import Flask


def create_app():
    app = Flask(__name__)

    secret_key = os.getenv("SECRET_KEY")

    if not secret_key:
        raise RuntimeError("SECRET_KEY environment variable is not set")

    app.config["SECRET_KEY"] = secret_key

    from .routes import main
    app.register_blueprint(main)

    return app
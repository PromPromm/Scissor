from flask import Flask
from flask_restx import Api

from .config import config_dict


def create_app(config=config_dict["dev"]):
    app = Flask(__name__)
    app.config.from_object(config)
    api = Api(
        app,
        title="Scissor API",
        description="A simple URL shortening REST API service",
    )
    return app

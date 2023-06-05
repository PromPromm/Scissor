from flask import Flask
from flask_restx import Api
from .utils import db
from flask_migrate import Migrate
from .utils import db
from .models.urls import Url
from .models.users import User
from .models.blocklist import TokenBlocklist

from .config import config_dict


def create_app(config=config_dict["dev"]):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)

    api = Api(
        app,
        title="Scissor API",
        description="A simple URL shortening REST API service",
    )

    migrate = Migrate(app, db)
    return app

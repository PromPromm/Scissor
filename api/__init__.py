from flask import Flask
from flask_restx import Api
from .utils import db
from flask_migrate import Migrate
from .utils import db
from .models.urls import Url
from .models.users import User
from .models.blocklist import TokenBlocklist
from .auth.views import auth_namespace
from .user.views import user_namespace
from flask_jwt_extended import JWTManager
from decouple import config as configuration

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

    api.add_namespace(auth_namespace)
    api.add_namespace(user_namespace)

    migrate = Migrate(app, db)

    jwt = JWTManager(app)

    @jwt.additional_claims_loader
    def add_claim_to_jwt(identity):
        email = User.get_by_id(identity).email
        if email == configuration("EMAIL"):
            return {"super_admin": True}
        return {"super_admin": False}

    return app

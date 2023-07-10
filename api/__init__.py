from flask import Flask
from flask_restx import Api
from .utils import db, limiter
from flask_migrate import Migrate
from .utils import db, mail, cache
from .models.urls import Url
from .models.users import User
from .models.token import ResetPasswordTokenBlocklist
from .models.blocklist import TokenBlocklist
from .auth.views import auth_namespace
from .user.views import user_namespace
from .urls.views import url_namespace

# from .payments.views import payment_namespace
from flask_jwt_extended import JWTManager
from decouple import config as configuration

# import stripe

from .config import config_dict

from logging.config import dictConfig

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                "datefmt": "%B %d, %Y %H:%M:%S %Z",
            }
        },
        "handlers": {
            "time-rotate": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "filename": "urlshortener.log",
                "when": "D",
                "interval": 10,
                "backupCount": 5,
                "formatter": "default",
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": "flask.log",
                "formatter": "default",
            },
        },
        "root": {"level": "INFO", "handlers": ["time-rotate"]},
    }
)


def create_app(config=config_dict["dev"]):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)

    authorization = {
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Add a JWT token to the header with ** Bearer &lt;JWT&gt; token to authorize **",
        }
    }

    api = Api(
        app,
        title="Scissor API",
        description="A simple URL shortening REST API service",
        authorizations=authorization,
        security="Bearer Auth",
    )

    api.add_namespace(auth_namespace)
    api.add_namespace(user_namespace)
    api.add_namespace(url_namespace)
    # api.add_namespace(payment_namespace)

    migrate = Migrate(app, db)

    # stripe.api_key = configuration("STRIPE_SECRET_KEY")

    mail.init_app(app)

    cache.init_app(app)

    limiter.init_app(app)

    jwt = JWTManager(app)

    @jwt.additional_claims_loader
    def add_claim_to_jwt(identity):
        email = User.get_by_id(identity).email
        if email == configuration("EMAIL"):
            return {"super_admin": True}
        return {"super_admin": False}

    return app

from flask_restx import Namespace, Resource, fields
from flask import request, abort, url_for
from ..models.users import User
from ..models.blocklist import TokenBlocklist
from werkzeug.security import generate_password_hash, check_password_hash
from http import HTTPStatus
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from ..utils import db, generate_confirmation_token, mail
from datetime import timezone, datetime
import validators
from flask_mail import Message

from flask import current_app as app

auth_namespace = Namespace("auth", "Namespace for authentication")

signup_model = auth_namespace.model(
    "signup",
    {
        "username": fields.String(required=True, description="A username"),
        "email": fields.String(required=True, description="An email"),
        "password": fields.String(required=True, description="A password"),
        "first_name": fields.String(required=True, description="First Name"),
        "last_name": fields.String(required=True, description="Last Name"),
    },
)

login_model = auth_namespace.model(
    "login",
    {
        "email": fields.String(required=True, description="Email"),
        "password": fields.String(required=True, description="Password"),
    },
)


def send_register_email(user, confirm_url):
    msg = Message(
        "Scissor-Please confirm your email",
        sender="noreply@demo.com",
        recipients=[user.email],
        body=f"Welcome to Scissor.Your account with username {user.username} has been created successfully."
        "Welcome! Thanks for signing up. Please follow this link to activate your account:"
        f"<a href='{confirm_url}'>Confirm Email</a>"
        "<br>"
        "<p>Cheers!</p>",
    )
    mail.send(msg)


@auth_namespace.route("/signup")
class SignUp(Resource):
    @auth_namespace.expect(signup_model)
    # @auth_namespace.marshal_with(signup_model, HTTPStatus.OK)
    @auth_namespace.doc(description="Sign up on Scissor")
    def post(self):
        """
        Register a user
        """
        data = request.get_json()

        if not validators.email(data.get("email")):
            abort(400, "Email is not valid")

        user = User.query.filter_by(email=data.get("email")).first()
        user_name = User.query.filter_by(username=data.get("username")).first()

        if user:
            app.logger.info(f"Someone tried to sign up with existing email")
            return {"Error": "User exists"}, HTTPStatus.CONFLICT
        if user_name:
            app.logger.info(
                f"Someone tried to sign up with a username already taken by someone else"
            )
            return {"message": "Username already in use"}, HTTPStatus.CONFLICT
        new_user = User(
            username=data.get("username"),
            email=data.get("email"),
            password=generate_password_hash(data.get("password")),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            confirmed=False,
        )
        db.session.add(new_user)
        token = generate_confirmation_token(new_user.email)
        confirm_url = url_for(
            "user_confirm_email_view",
            token=token,
            _external=True,
            _method="PATCH",
        )
        send_register_email(new_user, confirm_url)
        app.logger.info(f"Sign up email was sent to User {new_user.username}")
        db.session.commit()
        app.logger.info(f"User {new_user.username} signed up")
        return {"message": "User successfully created"}, HTTPStatus.CREATED


@auth_namespace.route("/login")
class Login(Resource):
    @auth_namespace.expect(login_model)
    @auth_namespace.doc(description="Login to account")
    def post(self):
        """
        Login a user
        """
        data = request.get_json()
        email = data.get("email")
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, data.get("password")):
            if user.is_admin:
                access_token = create_access_token(
                    identity=user.id,
                    fresh=True,
                    additional_claims={"is_administrator": True},
                )
                refresh_token = create_refresh_token(
                    identity=user.id, additional_claims={"is_administrator": True}
                )
                app.logger.info(f"Admin {user.username} logged in")
            else:
                access_token = create_access_token(
                    identity=user.id,
                    fresh=True,
                    additional_claims={"is_administrator": False},
                )
                refresh_token = create_refresh_token(
                    identity=user.id, additional_claims={"is_administrator": False}
                )
                app.logger.info(f"User {user.username} logged in")
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
            }, HTTPStatus.OK
        app.logger.info("User tried to login with incorrect details")
        return {"Error": "Invalid credentials"}, HTTPStatus.FORBIDDEN


@auth_namespace.route("/logout")
class Logout(Resource):
    @jwt_required(fresh=True)
    @auth_namespace.doc(description="Logs out user and revokes jwt")
    def delete(self):
        """
        Logout a user and blacklist jwt token
        """
        jti = get_jwt()["jti"]
        user = User.get_by_id(get_jwt_identity())
        token = TokenBlocklist(jti=jti, created_at=datetime.now(timezone.utc))
        db.session.add(token)
        db.session.commit()
        app.logger.info(f"{user.username} logged out")
        return {"message": "User successfully logged out"}


@auth_namespace.route("/refresh")
class Refresh(Resource):
    @jwt_required(refresh=True)
    @auth_namespace.doc(description="Generate refresh tokens")
    def post(self):
        """
        Generates refresh token
        """
        user_id = get_jwt_identity()
        user = User.get_by_id(user_id)
        if user.is_admin:
            access_token = create_access_token(
                identity=user_id,
                fresh=False,
                additional_claims={"is_administrator": True},
            )
            app.logger.info(f"Admin {user.username} got a jwt refresh token")
            return {"access_token": access_token}, HTTPStatus.OK
        access_token = create_access_token(
            identity=user_id, fresh=False, additional_claims={"is_administrator": False}
        )
        app.logger.info(f"User {user.username} got a jwt refresh token")
        return {"access_token": access_token}, HTTPStatus.OK

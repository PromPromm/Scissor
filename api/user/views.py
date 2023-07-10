from flask_restx import Namespace, Resource, fields, marshal
from flask import request, url_for, abort, copy_current_request_context
from ..models.users import User
from ..models.token import ResetPasswordTokenBlocklist
from flask_jwt_extended import jwt_required, get_jwt_identity
from http import HTTPStatus
from ..utils import (
    db,
    confirm_token,
    mail,
    admin_required,
    super_admin_required,
    cache,
    limiter,
)
from datetime import datetime
from flask_mail import Message
from decouple import config as configuration
from werkzeug.security import generate_password_hash, check_password_hash
from threading import Thread

from flask import current_app as app

user_namespace = Namespace("user", "Namespace for user")

url_model = user_namespace.model(
    "url",
    {
        "id": fields.Integer(),
        "name": fields.String(description="Name of shortened url"),
        "key": fields.String(description="Shortened url key"),
        "target_url": fields.String(description="Target URL"),
        "clicks": fields.Integer(),
        "user_id": fields.Integer(),
    },
)

user_model = user_namespace.model(
    "user",
    {
        "id": fields.Integer(),
        "username": fields.String(required=True, description="Username"),
        "email": fields.String(required=True, description="Email"),
        "first_name": fields.String(required=True, description="Firstname"),
        "last_name": fields.String(required=True, description="Lastname"),
        "paid": fields.Boolean(description="User subscription status"),
        "date_created": fields.DateTime(description="Date user joined"),
        "urls": fields.List(
            fields.Nested(url_model),
            required=True,
            description="List of shortened urls by user",
        ),
    },
)
change_password_model = user_namespace.model(
    "password_reset",
    {
        "new_password": fields.String(required=True, description="The new password"),
        "confirm_password": fields.String(
            required=True, description="The new password again"
        ),
    },
)

password_reset_request_model = user_namespace.model(
    "password_reset_request",
    {
        "email": fields.String(required=True, description="Email"),
    },
)


def send_async_reset(user):
    token = user.get_reset_token()
    msg = Message(
        "Scissor Password Reset",
        sender="noreply@demo.com",
        recipients=[user.email],
        body=f"""Hi {user.first_name} {user.last_name},
        A password reset for your account was requested.
        Please visit the following link to change your password
        {url_for(
            "user_change_password",
            token=token,
            _external=True,
            _method="PUT",
        )}
        Note that this link is valid for 24 hours.
        After the time limit has expired, you will have to resubmit the request for a password reset.
        """,
    )

    @copy_current_request_context
    def send_message(msg):
        mail.send(msg)

    sender = Thread(name="mail_sender", target=send_message, args=(msg,))
    sender.start()


@user_namespace.route("/")
class UserList(Resource):
    @user_namespace.doc(
        description="Get all registered users. Can be accessed by only an admin"
    )
    @admin_required()
    @cache.cached(timeout=1800)
    def get(self):
        """
        Get all users
        """
        users = User.query.all()
        return marshal(users, user_model), 200


@user_namespace.route("/<int:user_id>")
class UserView(Resource):
    @user_namespace.doc(
        description="""Get a user with the user id.
        This route can be accessed by an admin or the user whose id is in the user_id variable of the url.""",
        params={"user_id": "The user id"},
    )
    @jwt_required()
    def get(self, user_id):
        """
        Get a user by id
        """
        identity = get_jwt_identity()
        jwt_user = User.get_by_id(identity)
        user = User.get_by_id(user_id)

        # checks if it is an admin or the user whose id is in the user_id variable of the url that is accessing the route
        if (jwt_user.is_admin == True) or (identity == user_id):
            app.logger.info(f"A user's detail was gotten")
            return marshal(user, user_model), HTTPStatus.OK
        return {"message": "Not allowed."}, HTTPStatus.FORBIDDEN

    @user_namespace.doc(
        description="Delete a user with the user id. Only admins can access this route. Super Admin cannot be deleted",
        params={"user_id": "The user id"},
    )
    @admin_required()
    def delete(self, user_id):
        """
        Delete a user
        """
        user = User.get_by_id(user_id)

        # checks if admin is trying to delete the super administrator
        if user.email == configuration("EMAIL"):
            return {
                "Message": "You cannot delete the super administrator"
            }, HTTPStatus.FORBIDDEN
        db.session.delete(user)
        app.logger.info(f"Admin deleted user {User.get_by_id(user_id).username}")
        db.session.commit()
        return {"message": "User deleted successfully"}, HTTPStatus.OK

    @super_admin_required()
    @user_namespace.doc(
        description="Give or remove a user admin privileges using the user id. Only the super administrator can access this route",
        params={"user_id": "The user id"},
    )
    def patch(self, user_id):
        """
        Give or revoke staff privileges to user
        """
        user = User.get_by_id(user_id)

        # check if user is an admin
        if user.is_admin:
            user.remove_admin()
            app.logger.info("Super Admin removed a user's admin privilege")
            return {"messsage": "User is no longer an admin"}, HTTPStatus.OK
        user.make_admin()
        app.logger.info("Super Admin gave a user admin privilege")
        return {"messsage": "User is now an admin"}, HTTPStatus.OK


@user_namespace.route("/<int:user_id>/urls")
class UserURLsList(Resource):
    @jwt_required()
    @user_namespace.doc(
        description="""Get all the shortened urls a user has created.
        This route can be accessed by an admin or the user whose id is in the user_id variable of the url.""",
        params={"user_id": "The user id"},
    )
    @cache.cached(timeout=3600)
    def get(self, user_id):
        """
        Get a user's url history
        """
        identity = get_jwt_identity()
        jwt_user = User.get_by_id(identity)
        user = User.get_by_id(user_id)

        # checks if it is an admin or the user whose id is in the user_id variable of the url that is accessing the route
        if (jwt_user.is_admin == True) or (identity == user_id):
            urls = user.urls
            app.logger.info(f"Admin searched for all urls by {user.username}")
            return marshal(urls, url_model), HTTPStatus.OK
        return {"message": "Not allowed."}, HTTPStatus.FORBIDDEN


@user_namespace.route("/<int:user_id>/paid")
class PaidUserView(Resource):
    @user_namespace.doc(
        description="Give a user paid user privileges. Can be accessed by only an admin",
        params={"user_id": "The user id"},
    )
    @admin_required()
    def patch(self, user_id):
        """
        Give a user paid user privileges.
        """
        user = User.get_by_id(user_id)
        user.paid = True
        db.session.commit()
        app.logger.info(f"User {user.username} paid for a subsription plan")
        return {"Message": "Now a paid user"}, HTTPStatus.OK


@user_namespace.route("/<int:user_id>/paid_remove")
class RevokePaidUserView(Resource):
    @user_namespace.doc(
        description="Revoke a user paid user privileges. Can be accessed by only an admin",
        params={"user_id": "The user id"},
    )
    @admin_required()
    def patch(self, user_id):
        """
        Revoke a user's paid user privileges.
        """
        user = User.get_by_id(user_id)
        user.paid = False
        db.session.commit()
        app.logger.info(f"User {user.username} is now on the free plan")
        return {"Message": "No longer a paid user"}, HTTPStatus.OK


@user_namespace.route("/confirm/<token>")
class ConfirmEmailView(Resource):
    @user_namespace.doc(
        description="Confirms a user email.",
        params={"token": "The token contained the url sent to the user's email"},
    )
    def patch(self, token):
        """
        Confirm user email
        """

        # checks if token is valid
        if confirm_token(token):
            email = confirm_token(token)
            user = User.query.filter_by(email=email).first_or_404()

            # checks if user is already confirmed
            if user.confirmed:
                return {"message": "Account already confirmed"}, HTTPStatus.OK
            user.confirmed = True
            user.confirmed_on = datetime.now()
            db.session.commit()
            return {
                "message": "You have successfully confirmed your account. Thanks!"
            }, HTTPStatus.OK
        return {"Error": "The confirmation link is invalid or has expired."}, 498


@user_namespace.route("/reset_password_request")
class ResetPasswordRequest(Resource):
    @user_namespace.expect(password_reset_request_model)
    @user_namespace.doc(description="Reset Password Request on Scissor")
    @limiter.limit("1/day")  # Comment this line out when testing
    def post(self):
        """
        Request a password reset email
        """
        data = request.get_json()
        user = User.query.filter_by(email=data.get("email")).first_or_404()
        send_async_reset(user)
        return {"message": "Password Reset Email sent. Check your email"}, HTTPStatus.OK


@user_namespace.route("/reset_password/<token>")
class ChangePassword(Resource):
    @user_namespace.expect(change_password_model)
    @user_namespace.doc(
        description="Change user password.",
        params={"token": "The token contained the url sent to the user's email"},
    )
    def put(self, token):
        """
        Change password route
        """
        user = User.verify_reset_token(token)
        token_exists = ResetPasswordTokenBlocklist.query.filter_by(token=token).first()

        # checks if token has been blocklisted
        if token_exists:
            abort(400, "Token has already been used. Request another")

        # checks if user exists
        if user:
            data = request.get_json()
            # checks if new password and confirm password matches
            if data.get("new_password") == data.get("confirm_password"):
                # checks if the new password and old password are the same
                if check_password_hash(user.password, data.get("new_password")):
                    return {
                        "Error": "New password is the same as the old password. Kindly enter another password"
                    }, HTTPStatus.BAD_REQUEST
                new_token = ResetPasswordTokenBlocklist(token=token)
                db.session.add(new_token)
                user.password = generate_password_hash(data.get("new_password"))
                db.session.commit()
                return {
                    "message": "Password successfully changed. Proceed to login"
                }, HTTPStatus.OK
            return {
                "Error": "New password and confirm password do not match. Kindly enter password again"
            }, HTTPStatus.BAD_REQUEST
        return {"Error": "The reset token is invalid or has expired."}, 498

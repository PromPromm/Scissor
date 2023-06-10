from flask_restx import Namespace, Resource, fields
from flask import abort
from ..models.users import User
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from http import HTTPStatus
from ..utils import db, confirm_token
from datetime import datetime

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


@user_namespace.route("/")
class UserList(Resource):
    @user_namespace.marshal_with(user_model)
    @user_namespace.doc(
        description="Get all registered users. Can be accessed by only an admin"
    )
    @jwt_required()
    def get(self):
        """
        Get all users
        """
        users = User.query.all()
        return users, HTTPStatus.OK


@user_namespace.route("/<int:user_id>")
class UserView(Resource):
    @jwt_required()
    @user_namespace.marshal_with(user_model)
    @user_namespace.doc(
        description="Get a user with the user id. Only admins can access this route",
        params={"user_id": "The user id"},
    )
    def get(self, user_id):
        """
        Get a user's details
        """
        admin_id = get_jwt_identity()
        staff = User.get_by_id(admin_id)
        if staff.is_admin:
            user = User.get_by_id(user_id)
            app.logger.info(f"Admin got a user's details")
            return user, HTTPStatus.OK
        app.logger.warning(f"Non admin tried to get a user's details")
        return {"Error": "NOT ALLOWED"}, HTTPStatus.UNAUTHORIZED

    @jwt_required(fresh=True)
    @user_namespace.doc(
        description="Delete a user with the user id. Only admins can access this route.",
        params={"user_id": "The user id"},
    )
    def delete(self, user_id):
        """
        Delete a user
        """
        admin_id = get_jwt_identity()
        user = User.get_by_id(admin_id)
        if user.is_admin:
            db.session.delete(User.get_by_id(user_id))
            db.session.commit()
            app.logger.info(f"Admin deleted user {User.get_by_id(user_id).username}")
            return {"message": "User deleted successfully"}, HTTPStatus.OK
        app.logger.warning(f"Non admin tried to delete a user")
        return {"Error": "NOT ALLOWED"}, HTTPStatus.UNAUTHORIZED

    @jwt_required()
    @user_namespace.doc(
        description="Give a user admin privileges using the user id. Only the super administrator can access this route",
        params={"user_id": "The user id"},
    )
    def patch(self, user_id):
        """
        Give staff privileges to user
        """
        jwt = get_jwt()
        if not jwt.get("super_admin"):
            abort(401, "Admin privilege only")
        user = User.get_by_id(user_id)
        user.make_admin()
        app.logger.info("Super Admin gave a user admin privilege")
        return {"messsage": "User is now an admin"}, HTTPStatus.OK


@user_namespace.route("/<int:user_id>/urls")
class UserURLsList(Resource):
    @jwt_required()
    @user_namespace.marshal_list_with(url_model)
    @user_namespace.doc(
        description="Get all the shortened urls a user has created",
        params={"user_id": "The user id"},
    )
    def get(self, user_id):
        """
        Get a user's url history
        """
        user = User.get_by_id(user_id)
        urls = user.urls
        app.logger.info(f"Admin searched for all urls by {user.username}")
        return urls, HTTPStatus.OK


@user_namespace.route("/<int:user_id>/paid")
class PaidUserView(Resource):
    @user_namespace.doc(
        description="Give a user paid user privileges. Can be accessed by only an admin",
        params={"user_id": "The user id"},
    )
    @jwt_required()
    def patch(self, user_id):
        """
        Give a user paid user privileges.
        """
        user = User.get_by_id(user_id)
        user.paid = True
        db.session.commit()
        app.logger.info(f"User {user.username} paid for a subsription plan")
        return {"Message": "Now a paid user"}, HTTPStatus.OK


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
        if confirm_token(token):
            email = confirm_token(token)
            user = User.query.filter_by(email=email).first_or_404()
            if user.confirmed:
                return {"message": "Account already confirmed"}, HTTPStatus.OK
            user.confirmed = True
            user.confirmed_on = datetime.now()
            db.session.commit()
            return {
                "message": "You have successfully confirmed your account. Thanks!"
            }, HTTPStatus.OK
        return {"Error": "The confirmation link is invalid or has expired."}, 498

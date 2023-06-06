from flask_restx import Namespace, Resource, fields
from flask import abort
from ..models.users import User
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from http import HTTPStatus
from ..utils import db

user_namespace = Namespace("user", "Namespace for user")

url_model = user_namespace.model(
    "url",
    {
        "id": fields.Integer(),
        "name": fields.String(description="Name of shortened url"),
        "key": fields.String(description="Shortened url key"),
        "target url": fields.String(description="Target URL"),
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
            return user, HTTPStatus.OK
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
            return {"message": "User deleted successfully"}, HTTPStatus.OK
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
        return {"messsage": "User is now an admin"}, HTTPStatus.OK


@user_namespace.route("/<int:user_id>/urls")
class UserURLsList(Resource):
    @jwt_required()
    @user_namespace.marshal_list_with(url_model)
    @user_namespace.doc(
        description="Get the shortened urls a user has created",
        params={"user_id": "The user id"},
    )
    def get(self, user_id):
        """
        Get a user's url history
        """
        user = User.get_by_id(user_id)
        urls = user.urls
        return urls, HTTPStatus.OK

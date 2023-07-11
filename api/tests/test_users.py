import unittest
from ..config import config_dict
from ..utils import db
from .. import create_app
from flask_jwt_extended import create_access_token
from ..models.users import User
from decouple import config as configuration


class UserTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config=config_dict["test"])
        self.appctx = self.app.app_context()
        self.appctx.push()
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        db.drop_all()
        self.appctx.pop()
        self.app = None
        self.client = None

    def test_get_all_users(self):
        user_signup_data = {
            "first_name": "Test",
            "last_name": "Admin",
            "email": "testadmin@gmail.com",
            "username": "admin",
            "password": "password",
        }
        self.client.post("signup", json=user_signup_data)

        admin = User.query.filter_by(email="testadmin@gmail.com").first()

        token = create_access_token(
            identity=admin.id, additional_claims={"is_administrator": True}
        )

        headers = {"Authorization": f"Bearer {token}"}

        response = self.client.get("users", headers=headers)
        assert response.status_code == 200
        assert len(response.json) == 1

    def test_get_user_by_id(self):
        admin_signup_data = {
            "first_name": "Test",
            "last_name": "Admin",
            "email": "testadmin@gmail.com",
            "username": "admin",
            "password": "password",
        }

        self.client.post("signup", json=admin_signup_data)

        admin = User.query.filter_by(email="testadmin@gmail.com").first()

        token = create_access_token(
            identity=admin.id, additional_claims={"is_administrator": True}
        )

        headers = {"Authorization": f"Bearer {token}"}

        response = self.client.get("/user/1", headers=headers)

        assert response.status_code == 200

        assert response.json["email"] == "testadmin@gmail.com"

    def test_delete_user_by_id(self):
        admin_signup_data = {
            "first_name": "Test",
            "last_name": "Admin",
            "email": "testadmin@gmail.com",
            "username": "admin",
            "password": "password",
        }

        self.client.post("signup", json=admin_signup_data)

        admin = User.query.filter_by(email="testadmin@gmail.com").first()

        token = create_access_token(
            identity=admin.id, additional_claims={"is_administrator": True}
        )

        headers = {"Authorization": f"Bearer {token}"}

        response = self.client.delete("/user/1", headers=headers)

        assert response.status_code == 200

        assert response.json == {"message": "User deleted successfully"}

    def test_patch_user_by_id(self):
        admin_signup_data = {
            "first_name": "Test",
            "last_name": "Admin",
            "email": configuration("EMAIL"),
            "username": "admin",
            "password": "password",
        }
        self.client.post("signup", json=admin_signup_data)

        admin = User.query.filter_by(email=configuration("EMAIL")).first()

        token = create_access_token(identity=admin.id)

        headers = {"Authorization": f"Bearer {token}"}

        response = self.client.patch("/user/1", headers=headers)

        assert response.status_code == 200

        assert response.json == {"messsage": "User is now an admin"}

    def test_user_urls(self):
        user_signup_data = {
            "first_name": "Test",
            "last_name": "Admin",
            "email": "testadmin@gmail.com",
            "username": "admin",
            "password": "password",
        }
        self.client.post("signup", json=user_signup_data)

        admin = User.query.filter_by(email="testadmin@gmail.com").first()

        token = create_access_token(
            identity=admin.id, additional_claims={"is_administrator": True}
        )

        headers = {"Authorization": f"Bearer {token}"}
        url_post_data = {
            "name": "Google",
            "target url": "https://www.google.com/",
        }

        self.client.post("/create", headers=headers, json=url_post_data)

        response = self.client.get("/user/1/urls", headers=headers)

        assert response.status_code == 200

        assert len(response.json) == 1

    def test_revoke_paid(self):
        user_signup_data = {
            "first_name": "Test",
            "last_name": "Admin",
            "email": "testadmin@gmail.com",
            "username": "admin",
            "password": "password",
        }
        self.client.post("signup", json=user_signup_data)

        admin = User.query.filter_by(email="testadmin@gmail.com").first()

        token = create_access_token(
            identity=admin.id, additional_claims={"is_administrator": True}
        )

        headers = {"Authorization": f"Bearer {token}"}

        response = self.client.patch("1/paid_remove", headers=headers)

        assert response.status_code == 200

        assert response.json == {"Message": "No longer a paid user"}

    def test_confirm_email(self):
        user_signup_data = {
            "first_name": "Test",
            "last_name": "Admin",
            "email": "testadmin@gmail.com",
            "username": "admin",
            "password": "password",
        }
        self.client.post("/auth/signup", json=user_signup_data)

        response = self.client.patch("confirm/paid_remove")

        assert response.status_code == 498

        assert response.json == {
            "Error": "The confirmation link is invalid or has expired."
        }

    def test_reset_request(self):
        user_signup_data = {
            "first_name": "Test",
            "last_name": "Admin",
            "email": "testadmin@gmail.com",
            "username": "admin",
            "password": "password",
        }
        self.client.post("signup", json=user_signup_data)
        reset_password_data = {"email": "testadmin@gmail.com"}
        response = self.client.post("reset_password_request", json=reset_password_data)
        assert response.json == {
            "message": "Password Reset Email sent. Check your email"
        }
        assert response.status_code == 200

    def test_change_password(self):
        user_signup_data = {
            "first_name": "Test",
            "last_name": "Admin",
            "email": "testadmin@gmail.com",
            "username": "admin",
            "password": "password",
        }
        self.client.post("signup", json=user_signup_data)
        change_password_data = {
            "new_password": "password",
            "confirm_password": "password",
        }
        response = self.client.put("reset_password/token", json=change_password_data)

        assert response.status_code == 498

        assert response.json == {"Error": "The reset token is invalid or has expired."}

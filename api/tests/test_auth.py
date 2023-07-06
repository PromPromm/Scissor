import unittest
from ..config import config_dict
from ..utils import db
from .. import create_app
from flask_jwt_extended import create_refresh_token, create_access_token
from ..models.users import User


class AuthenticationTestCase(unittest.TestCase):
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

    def test_user_signup(self):
        user_signup_data = {
            "first_name": "Test",
            "last_name": "Admin",
            "email": "testadmin@gmail.com",
            "username": "admin",
            "password": "password",
        }

        response = self.client.post("/auth/signup", json=user_signup_data)
        assert response.status_code == 201

    def test_user_login(self):
        user_signup_data = {
            "first_name": "Test",
            "last_name": "Admin",
            "email": "testadmin@gmail.com",
            "username": "admin",
            "password": "password",
        }
        response = self.client.post("/auth/signup", json=user_signup_data)
        user_login_data = {
            "email": "testadmin@gmail.com",
            "password": "password",
        }
        response = self.client.post("/auth/login", json=user_login_data)
        assert response.status_code == 200

    def test_user_refresh(self):
        admin_signup_data = {
            "first_name": "Test",
            "last_name": "Admin",
            "email": "testadmin@gmail.com",
            "username": "admin",
            "password": "password",
        }

        response = self.client.post("/auth/signup", json=admin_signup_data)

        admin = User.query.filter_by(email="testadmin@gmail.com").first()

        token = create_refresh_token(identity=admin.id)
        header = {"Authorization": f"Bearer {token}"}

        response = self.client.post("/auth/refresh", headers=header)

        assert response.status_code == 200

    def test_user_logout(self):
        admin_signup_data = {
            "first_name": "Test",
            "last_name": "Admin",
            "email": "testadmin@gmail.com",
            "username": "admin",
            "password": "password",
        }

        response = self.client.post("/auth/signup", json=admin_signup_data)

        admin = User.query.filter_by(email="testadmin@gmail.com").first()

        token = create_access_token(identity=admin.id, fresh=True)

        header = {"Authorization": f"Bearer {token}"}

        response = self.client.delete("/auth/logout", headers=header)
        assert response.status_code == 200
        assert response.json == {"message": "User successfully logged out"}

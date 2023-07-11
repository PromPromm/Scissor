import unittest
from ..config import config_dict
from ..utils import db
from .. import create_app
from flask_jwt_extended import create_access_token
from ..models.users import User
from ..models.urls import Url


class URLTestCase(unittest.TestCase):
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

    def test_url_post(self):
        user_signup_data = {
            "first_name": "Test",
            "last_name": "Admin",
            "email": "testadmin@gmail.com",
            "username": "admin",
            "password": "password",
        }
        self.client.post("signup", json=user_signup_data)

        admin = User.query.filter_by(email="testadmin@gmail.com").first()

        token = create_access_token(identity=admin.id)

        headers = {"Authorization": f"Bearer {token}"}
        url_post_data = {
            "name": "Google",
            "target url": "https://www.google.com/",
        }

        response = self.client.post("/create", headers=headers, json=url_post_data)

        assert response.status_code == 201

    def test_url_get(self):
        user_signup_data = {
            "first_name": "Test",
            "last_name": "Admin",
            "email": "testadmin@gmail.com",
            "username": "admin",
            "password": "password",
        }
        self.client.post("signup", json=user_signup_data)

        admin = User.query.filter_by(email="testadmin@gmail.com").first()

        token = create_access_token(identity=admin.id)

        headers = {"Authorization": f"Bearer {token}"}
        url_post_data = {
            "name": "Google",
            "target url": "https://www.google.com/",
        }

        self.client.post("/create", headers=headers, json=url_post_data)

        url = Url.query.get_or_404(1)

        response = self.client.get(f"{url.key}")

        assert response.json == None

        assert response.status_code == 302  # Redirect status code

    def test_url_delete(self):
        user_signup_data = {
            "first_name": "Test",
            "last_name": "Admin",
            "email": "testadmin@gmail.com",
            "username": "admin",
            "password": "password",
        }
        self.client.post("signup", json=user_signup_data)

        admin = User.query.filter_by(email="testadmin@gmail.com").first()

        token = create_access_token(identity=admin.id)

        headers = {"Authorization": f"Bearer {token}"}
        url_post_data = {
            "name": "Google",
            "target url": "https://www.google.com/",
        }

        self.client.post("/create", headers=headers, json=url_post_data)

        url = Url.query.get_or_404(1)

        response = self.client.delete(f"{url.key}", headers=headers)

        assert response.json == {"message": "Url has been deleted"}
        assert response.status_code == 200

    def test_qrcode(self):
        user_signup_data = {
            "first_name": "Test",
            "last_name": "Admin",
            "email": "testadmin@gmail.com",
            "username": "admin",
            "password": "password",
        }
        self.client.post("signup", json=user_signup_data)

        admin = User.query.filter_by(email="testadmin@gmail.com").first()

        token = create_access_token(identity=admin.id)

        headers = {"Authorization": f"Bearer {token}"}

        url_post_data = {
            "name": "Google",
            "target url": "https://www.google.com/",
        }

        self.client.post("/create", headers=headers, json=url_post_data)

        url = Url.query.get_or_404(1)

        response = self.client.post(f"{url.key}/qrcode")

        assert response.json == None
        assert response.status_code == 200

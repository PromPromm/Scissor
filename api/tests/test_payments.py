import unittest
from ..config import config_dict
from ..utils import db
from .. import create_app
from flask_jwt_extended import create_access_token
from ..models.users import User


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

    def test_payment(self):
        admin_signup_data = {
            "first_name": "Test",
            "last_name": "Admin",
            "email": "testadmin@gmail.com",
            "username": "admin",
            "password": "password",
        }
        self.client.post("/auth/signup", json=admin_signup_data)

        admin = User.query.filter_by(email="testadmin@gmail.com").first()

        token = create_access_token(identity=admin.id)

        headers = {"Authorization": f"Bearer {token}"}

        response = self.client.post("/payment/subscription/basic", headers=headers)

        assert response.json == None

        assert response.status_code == 303

    def test_payment_success(self):
        response = self.client.get("/payment/success")
        assert response.status_code == 200

    def test_payment_failure(self):
        response = self.client.get("/payment/cancel")
        assert response.status_code == 200

    def test_payment_event(self):
        headers = {"STRIPE_SIGNATURE": "Bearer"}
        response = self.client.post("/payment/event", headers=headers)
        assert response.status_code == 400

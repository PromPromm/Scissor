from ..utils import db
from datetime import datetime
import jwt
from time import time
import os
from flask import current_app as app


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(45), nullable=False)
    last_name = db.Column(db.String(45), nullable=False)
    username = db.Column(db.String(45), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    paid = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    urls = db.relationship("Url", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def make_admin(self):
        """
        Gives user admin privileges
        """
        self.is_admin = True
        db.session.commit()

    def remove_admin(self):
        """
        Gives user admin privileges
        """
        self.is_admin = False
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

    def get_reset_token(self, expires=86400):
        return jwt.encode(
            {"reset_password": self.username, "exp": time() + expires},
            key=os.getenv("SECRET_KEY"),
        )

    def verify_reset_token(token):
        try:
            username = jwt.decode(
                token, key=os.getenv("SECRET_KEY"), algorithms="HS256"
            )["reset_password"]
        except Exception as e:
            app.logger.info(e)
            return
        return User.query.filter_by(username=username).first()

from ..utils import db
from datetime import datetime


class ResetPasswordTokenBlocklist(db.Model):
    __tablename__ = "reset_password_token"
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())

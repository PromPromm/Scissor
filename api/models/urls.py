from ..utils import db
from datetime import datetime


class Url(db.Model):
    __tablename__ = "urls"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=True)
    key = db.Column(db.String, unique=True, index=True)
    target_url = db.Column(db.String, index=True)
    is_active = db.Column(db.Boolean, default=True)
    clicks = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __repr__(self):
        return f"<URL {self.name}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_by_key(cls, key):
        """
        A function to get a url instance by key
        """
        return cls.query.filter_by(key=key).first()

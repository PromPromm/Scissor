from .db import db
import string
import secrets
from ..models.urls import Url
from .mail import mail
from itsdangerous import URLSafeTimedSerializer
from decouple import config as configuration


def generate_url_key(num_of_chars: int):
    """
    Generate random string for free user url key
    """
    chars = string.ascii_uppercase + string.digits
    key = "".join(secrets.choice(chars) for _ in range(num_of_chars))

    while Url.get_by_key(key):
        key = generate_url_key(5)
    return key


def generate_confirmation_token(email):
    """
    Generates token for email confirmation
    """
    serializer = URLSafeTimedSerializer(configuration("SECRET_KEY"))
    return serializer.dumps(email, salt=configuration("SECURITY_PASSWORD_SALT"))


def confirm_token(token, expiration=3600):
    """
    Confirms token contained in the url
    """
    serializer = URLSafeTimedSerializer(configuration("SECRET_KEY"))
    try:
        email = serializer.loads(
            token, salt=configuration("SECURITY_PASSWORD_SALT"), max_age=expiration
        )
    except:
        return False
    return email

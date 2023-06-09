from .db import db
import string
import secrets
from ..models.urls import Url


def generate_url_key(num_of_chars: int):
    """
    Generate random string for free user url key
    """
    chars = string.ascii_uppercase + string.digits
    key = "".join(secrets.choice(chars) for _ in range(num_of_chars))

    while Url.get_by_key(key):
        key = generate_url_key(5)
    return key

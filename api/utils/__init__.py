from .db import db
from random import choice
import string


def generate_url_key(num_of_chars: int):
    """
    Generate random string for free user url key
    """
    return "".join(
        choice(string.ascii_letters + string.digits) for _ in range(num_of_chars)
    )

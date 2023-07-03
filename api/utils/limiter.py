from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from redis import Redis
from decouple import config as configuration

redis = Redis(host="localhost", port=6379)
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=configuration("RATELIMIT_STORAGE_URL"),
    storage_options={"socket_connect_timeout": 30},
    strategy="fixed-window",
)

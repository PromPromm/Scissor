from flask_caching import Cache

cache = Cache(config={"CACHE_TYPE": "flask_caching.backends.SimpleCache"})

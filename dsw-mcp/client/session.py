import requests

from utils.ssl import apply_ssl_verify

session = requests.Session()
apply_ssl_verify(session)

from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://dsw.kemenkeu.go.id")
THANG = os.getenv("THANG", "2026")
DSW_USER = os.getenv("DSW_USER")
DSW_PASSWORD = os.getenv("DSW_PASSWORD")
SSL_VERIFY = os.getenv("SSL_VERIFY", "true").lower() != "false"
SSL_CA_BUNDLE = os.getenv("SSL_CA_BUNDLE")

import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")

    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "mindtrends_uk")

    TRENDS_MODE = os.environ.get("TRENDS_MODE", "auto")  # auto | live | simulated
    TRENDS_CACHE_TTL_MINUTES = int(os.environ.get("TRENDS_CACHE_TTL_MINUTES", 60))
    TRENDS_REQUEST_TIMEOUT = int(os.environ.get("TRENDS_REQUEST_TIMEOUT", 15))

    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@mindtrends.uk")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "ChangeMe123!")
    ADMIN_NAME = os.environ.get("ADMIN_NAME", "System Administrator")

    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    UK_REGIONS = [
        {"code": "GB-ENG", "name": "England", "pytrends_geo": "GB-ENG"},
        {"code": "GB-SCT", "name": "Scotland", "pytrends_geo": "GB-SCT"},
        {"code": "GB-WLS", "name": "Wales", "pytrends_geo": "GB-WLS"},
        {"code": "GB-NIR", "name": "Northern Ireland", "pytrends_geo": "GB-NIR"},
        {"code": "GB", "name": "United Kingdom (All)", "pytrends_geo": "GB"},
    ]

from flask_login import LoginManager
from pymongo import MongoClient

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access the research dashboard."
login_manager.login_message_category = "warning"

mongo_client = None
db = None


def init_mongo(app):
    global mongo_client, db
    mongo_client = MongoClient(app.config["MONGO_URI"], serverSelectionTimeoutMS=5000)
    db = mongo_client[app.config["MONGO_DB_NAME"]]
    app.db = db
    _ensure_indexes(db)
    return db


def _ensure_indexes(db):
    db.users.create_index("email", unique=True)
    db.disorders.create_index("slug", unique=True)
    db.saved_analyses.create_index("user_id")
    db.trend_cache.create_index("cache_key", unique=True)
    db.activity_logs.create_index("created_at")

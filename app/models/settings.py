from app.extensions import db

DEFAULT_TIMEFRAMES = [
    {"label": "Last 12 months", "value": "today 12-m"},
    {"label": "Last 5 years", "value": "today 5-y"},
    {"label": "2015 - Present", "value": "2015-01-01 {today}"},
    {"label": "Since 2020", "value": "2020-01-01 {today}"},
]

DEFAULT_CATEGORIES = [
    {"name": "Health", "gtrends_id": 45},
    {"name": "Mental Health", "gtrends_id": 0},
    {"name": "Medical Conditions", "gtrends_id": 419},
]

DEFAULT_RETRIEVAL_SETTINGS = {
    "mode": "auto",  # auto | live | simulated
    "cache_ttl_minutes": 60,
    "request_timeout": 15,
    "max_retries": 2,
    "backoff_seconds": 5,
}


class Settings:
    @staticmethod
    def get_retrieval_settings():
        doc = db.app_settings.find_one({"key": "retrieval"})
        if doc:
            merged = {**DEFAULT_RETRIEVAL_SETTINGS, **doc.get("value", {})}
            return merged
        return dict(DEFAULT_RETRIEVAL_SETTINGS)

    @staticmethod
    def update_retrieval_settings(**fields):
        current = Settings.get_retrieval_settings()
        current.update({k: v for k, v in fields.items() if v is not None})
        db.app_settings.update_one(
            {"key": "retrieval"}, {"$set": {"value": current}}, upsert=True
        )
        return current

    @staticmethod
    def get_categories():
        doc = db.app_settings.find_one({"key": "categories"})
        if doc:
            return doc.get("value", DEFAULT_CATEGORIES)
        return list(DEFAULT_CATEGORIES)

    @staticmethod
    def set_categories(categories):
        db.app_settings.update_one(
            {"key": "categories"}, {"$set": {"value": categories}}, upsert=True
        )

    @staticmethod
    def get_timeframes():
        doc = db.app_settings.find_one({"key": "timeframes"})
        if doc:
            return doc.get("value", DEFAULT_TIMEFRAMES)
        return list(DEFAULT_TIMEFRAMES)

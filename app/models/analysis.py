from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId

from app.extensions import db


class SavedAnalysis:
    @staticmethod
    def create(user_id, title, params, summary=None):
        doc = {
            "user_id": ObjectId(user_id),
            "title": title.strip(),
            "params": params,
            "summary": summary or {},
            "created_at": datetime.now(timezone.utc),
        }
        result = db.saved_analyses.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    @staticmethod
    def for_user(user_id, limit=50):
        return list(
            db.saved_analyses.find({"user_id": ObjectId(user_id)})
            .sort("created_at", -1)
            .limit(limit)
        )

    @staticmethod
    def get(analysis_id, user_id=None):
        try:
            oid = ObjectId(analysis_id)
        except (InvalidId, TypeError):
            return None
        query = {"_id": oid}
        if user_id:
            query["user_id"] = ObjectId(user_id)
        return db.saved_analyses.find_one(query)

    @staticmethod
    def delete(analysis_id, user_id):
        db.saved_analyses.delete_one(
            {"_id": ObjectId(analysis_id), "user_id": ObjectId(user_id)}
        )

    @staticmethod
    def count():
        return db.saved_analyses.count_documents({})


class ActivityLog:
    @staticmethod
    def record(action, actor=None, details=None, level="info"):
        db.activity_logs.insert_one(
            {
                "action": action,
                "actor": actor,
                "details": details or {},
                "level": level,
                "created_at": datetime.now(timezone.utc),
            }
        )

    @staticmethod
    def recent(limit=200):
        return list(db.activity_logs.find().sort("created_at", -1).limit(limit))

    @staticmethod
    def count():
        return db.activity_logs.count_documents({})


class ContentPage:
    """Editable public content: about, methodology, faq, resources."""

    DEFAULTS = {
        "about": {
            "title": "About the Study",
            "body": (
                "This platform explores online search interest for common mental "
                "health disorders across the United Kingdom using Google Trends. "
                "It was built as an MSc research project to help researchers, "
                "students and the public understand how public search interest "
                "changes over time and by region."
            ),
        },
        "methodology": {
            "title": "Methodology",
            "body": (
                "Search-interest data is retrieved from Google Trends, which "
                "reports *relative* search interest on a 0-100 scale rather than "
                "absolute search volume. Time period, UK region and search "
                "category are configurable. Where live data is unavailable, the "
                "platform clearly labels simulated data used for demonstration."
            ),
        },
        "faq": {
            "title": "Frequently Asked Questions",
            "body": (
                "Q: Does this diagnose mental health conditions?\nA: No. This "
                "system analyses aggregate, anonymised search interest only; it "
                "does not diagnose, assess severity, or identify individuals.\n\n"
                "Q: Where does the data come from?\nA: Google Trends, via the "
                "unofficial PyTrends interface."
            ),
        },
        "resources": {
            "title": "Support Resources",
            "body": (
                "If you or someone you know is struggling, UK support is "
                "available from the NHS (111), Samaritans (116 123, free, "
                "24/7), Mind (0300 123 3393), and CALM (0800 58 58 58)."
            ),
        },
    }

    @staticmethod
    def get(key):
        doc = db.content_pages.find_one({"key": key})
        if doc:
            return doc
        default = ContentPage.DEFAULTS.get(key, {"title": key.title(), "body": ""})
        return {"key": key, **default}

    @staticmethod
    def all_keys():
        return list(ContentPage.DEFAULTS.keys())

    @staticmethod
    def update(key, title, body):
        db.content_pages.update_one(
            {"key": key},
            {
                "$set": {
                    "title": title,
                    "body": body,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
            upsert=True,
        )

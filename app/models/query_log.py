from datetime import datetime, timezone

from bson import ObjectId

from app.extensions import db


class SearchQuery:
    """Persists each researcher data-retrieval request (search_queries collection)."""

    @staticmethod
    def record(user_id, disorder_ids, regions, timeframe, category):
        doc = {
            "user_id": ObjectId(user_id) if user_id else None,
            "disorder_ids": disorder_ids,
            "regions": regions,
            "timeframe": timeframe,
            "category": category,
            "created_at": datetime.now(timezone.utc),
        }
        db.search_queries.insert_one(doc)
        return doc

    @staticmethod
    def count():
        return db.search_queries.count_documents({})

    @staticmethod
    def recent_for_user(user_id, limit=10):
        return list(
            db.search_queries.find({"user_id": ObjectId(user_id)})
            .sort("created_at", -1)
            .limit(limit)
        )

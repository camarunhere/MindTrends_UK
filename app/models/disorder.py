import re
from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId

from app.extensions import db


def slugify(text):
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


class Disorder:
    """Repository wrapper around the `disorders` collection."""

    @staticmethod
    def create(name, description, search_term, category="Health", gtrends_category=0):
        slug = slugify(name)
        doc = {
            "name": name.strip(),
            "slug": slug,
            "description": description.strip(),
            "search_term": search_term.strip() or name.strip(),
            "category": category.strip() or "Health",
            "gtrends_category": int(gtrends_category or 0),
            "active": True,
            "created_at": datetime.now(timezone.utc),
        }
        result = db.disorders.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    @staticmethod
    def all(active_only=False):
        query = {"active": True} if active_only else {}
        return list(db.disorders.find(query).sort("name", 1))

    @staticmethod
    def get_by_id(disorder_id):
        try:
            oid = ObjectId(disorder_id)
        except (InvalidId, TypeError):
            return None
        return db.disorders.find_one({"_id": oid})

    @staticmethod
    def get_by_slug(slug):
        return db.disorders.find_one({"slug": slug})

    @staticmethod
    def update(disorder_id, **fields):
        fields = {k: v for k, v in fields.items() if v is not None}
        if "name" in fields:
            fields["slug"] = slugify(fields["name"])
        db.disorders.update_one({"_id": ObjectId(disorder_id)}, {"$set": fields})

    @staticmethod
    def delete(disorder_id):
        db.disorders.delete_one({"_id": ObjectId(disorder_id)})

    @staticmethod
    def count():
        return db.disorders.count_documents({})

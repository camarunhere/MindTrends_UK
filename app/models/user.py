from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db

ROLE_VISITOR = "visitor"
ROLE_RESEARCHER = "researcher"
ROLE_ADMIN = "admin"


class User(UserMixin):
    def __init__(self, doc):
        self._doc = doc

    # -- Flask-Login required properties --
    def get_id(self):
        return str(self._doc["_id"])

    @property
    def is_active(self):
        return self._doc.get("active", True)

    # -- convenience accessors --
    @property
    def id(self):
        return str(self._doc["_id"])

    @property
    def name(self):
        return self._doc.get("name", "")

    @property
    def email(self):
        return self._doc.get("email", "")

    @property
    def role(self):
        return self._doc.get("role", ROLE_RESEARCHER)

    @property
    def institution(self):
        return self._doc.get("institution", "")

    @property
    def created_at(self):
        return self._doc.get("created_at")

    def is_admin(self):
        return self.role == ROLE_ADMIN

    def check_password(self, password):
        return check_password_hash(self._doc.get("password_hash", ""), password)

    def to_public_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "institution": self.institution,
            "active": self.is_active,
            "created_at": self.created_at,
        }

    # -- class / repository methods --
    @staticmethod
    def create(name, email, password, role=ROLE_RESEARCHER, institution=""):
        doc = {
            "name": name.strip(),
            "email": email.strip().lower(),
            "password_hash": generate_password_hash(password, method="pbkdf2:sha256"),
            "role": role,
            "institution": institution.strip(),
            "active": True,
            "created_at": datetime.now(timezone.utc),
        }
        result = db.users.insert_one(doc)
        doc["_id"] = result.inserted_id
        return User(doc)

    @staticmethod
    def get_by_id(user_id):
        try:
            oid = ObjectId(user_id)
        except (InvalidId, TypeError):
            return None
        doc = db.users.find_one({"_id": oid})
        return User(doc) if doc else None

    @staticmethod
    def get_by_email(email):
        doc = db.users.find_one({"email": email.strip().lower()})
        return User(doc) if doc else None

    @staticmethod
    def email_exists(email):
        return db.users.count_documents({"email": email.strip().lower()}) > 0

    @staticmethod
    def all(limit=500):
        return [User(d) for d in db.users.find().sort("created_at", -1).limit(limit)]

    @staticmethod
    def count():
        return db.users.count_documents({})

    def set_role(self, role):
        db.users.update_one({"_id": self._doc["_id"]}, {"$set": {"role": role}})
        self._doc["role"] = role

    def set_active(self, active):
        db.users.update_one({"_id": self._doc["_id"]}, {"$set": {"active": active}})
        self._doc["active"] = active

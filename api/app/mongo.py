import os

from pymongo import MongoClient
from pymongo.collection import Collection

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "msb_backend_lab")

client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)

mongo_db = client[MONGO_DATABASE]

activity_events = mongo_db["activity_events"]


def get_activity_collection() -> Collection:
    """Return the MongoDB collection used for activity/audit documents."""
    return activity_events

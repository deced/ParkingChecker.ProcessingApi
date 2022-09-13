import os

from pymongo import MongoClient
from dotenv import load_dotenv

Param = 10

load_dotenv("db_properties.env")

client = MongoClient(os.getenv("DB_URL"))
spotCollection = client.get_database(os.getenv("DATABASE_NAME")).get_collection(os.getenv("COLLECTION_NAME"))


def set_available(spot):
    spotCollection.update_one({"_id": spot['_id']},
                              {"$set": {"available": True}})


def inc_verification_count(spot):
    if spot["verificationCount"] >= int(os.getenv("VERIFICATION_COUNT")):
        spotCollection.update_one({"_id": spot['_id']}, {"$set": {"verificationCount": spot['verificationCount'] + 1, "approved": True}})
    else:
        spotCollection.update_one({"_id": spot['_id']}, {"$set": {"verificationCount": spot['verificationCount'] + 1}})


def dec_verification_count(spot):
    if spot["verificationCount"] <= 0:
        spotCollection.delete_one({"_id": spot['_id']})
    else:
        spotCollection.update_one({"_id": spot['_id']}, {"$set": {"verificationCount": spot['verificationCount'] - 1}})


def get_spots():
    return list(spotCollection.find({}))


def get_not_approved_spots():
    return list(spotCollection.find({"approved": False}))


def get_approved_spots():
    return list(spotCollection.find({"approved": True}))


def get_available_and_approved_spots():
    return list(spotCollection.find({"$and": [{"approved": True}, {"available": True}]}))


def create_parking(x1, y1, x2, y2):
    spot = {
        "x1": x1,
        "y1": y1,
        "x2": x2,
        "y2": y2,
        "verificationCount": 0,
        "available": False,
        "approved": False
    }
    spotCollection.insert_one(spot)

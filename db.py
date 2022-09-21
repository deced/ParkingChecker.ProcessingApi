import os
from datetime import datetime

from pymongo import MongoClient
from dotenv import load_dotenv

Param = 10

load_dotenv("db_properties.env")

client = MongoClient(os.getenv("DB_URL"))
spot_collection = client.get_database(os.getenv("DATABASE_NAME")).get_collection(os.getenv("SPOT_COLLECTION_NAME"))
parking_image_collection = client.get_database(os.getenv("DATABASE_NAME")).get_collection(os.getenv("PARKING_IMAGE_COLLECTION_NAME"))
output_image_collection = client.get_database(os.getenv("DATABASE_NAME")).get_collection(os.getenv("OUTPUT_IMAGE_COLLECTION_NAME"))


def set_available(spot):
    spot_collection.update_one({"_id": spot['_id']}, {"$set": {"available": False, "lastUpdate": datetime.now()}})
    # spot_collection.update_one({"_id": spot['_id']},
    #                            {"$set": {"available": True, "lastUpdate": datetime.now(),
    #                                      "x1": spot['x1'], "y1": spot['y1'], "x2": spot['x2'], "y2": spot['y2']}})


def set_not_available(spot):
    spot_collection.update_one({"_id": spot['_id']}, {"$set": {"available": False, "lastUpdate": datetime.now()}})
    # spot_collection.update_one({"_id": spot['_id']},
    #                            {"$set": {"available": False, "lastUpdate": datetime.now(),
    #                                      "x1": spot['x1'], "y1": spot['y1'], "x2": spot['x2'], "y2": spot['y2']}})

def save_image(path, parking_id):
    spot = {
        "creationDate": datetime.now(),
        "fullPath": path,
        "parkingId": parking_id
    }
    existing_image = output_image_collection.find_one({"parkingId": parking_id})
    if existing_image is None:
        output_image_collection.insert_one(spot)
    else:
        output_image_collection.update_one({"parkingId": parking_id},
                                   {"$set": {"fullPath": path, "creationDate": datetime.now() }})

def inc_verification_count(spot):
    if spot["verificationCount"] >= int(os.getenv("VERIFICATION_COUNT")):
        spot_collection.update_one({"_id": spot['_id']},
                                   {"$set": {"verificationCount": spot['verificationCount'] + 1, "approved": True,
                                            "lastUpdate": datetime.now()}})
    else:
        spot_collection.update_one({"_id": spot['_id']}, {
            "$set": {"verificationCount": spot['verificationCount'] + 1, "lastUpdate": datetime.now()}})


def dec_verification_count(spot):
    if spot["verificationCount"] <= 0:
        spot_collection.delete_one({"_id": spot['_id']})
    else:
        spot_collection.update_one({"_id": spot['_id']}, {
            "$set": {"verificationCount": spot['verificationCount'] - 1, "lastUpdate": datetime.now()}})


def get_spots(parkingId):
    return list(spot_collection.find({}))


def update(spot):
    spot_collection.update_one({"_id": spot['_id']}, {
        "$set": {"x1": spot["x1"],
                 "x2": spot["x2"],
                 "y1": spot["y1"],
                 "y2": spot["y2"],
                 "verificationCount": spot["verificationCount"],
                 "available": spot["available"],
                 "approved": spot["approved"],
                 "lastUpdate": datetime.now(),
                 "parkingId": spot["parkingId"]}})


def get_not_approved_spots(parking_id):
    return list(spot_collection.find({"$and": [{"approved": False}, {"parkingId": parking_id}]}))


def get_approved_spots(parking_id):
    return list(spot_collection.find({"$and": [{"approved": True}, {"parkingId": parking_id}]}))


def get_available_and_approved_spots(parking_id):
    return list(spot_collection.find({"$and": [{"approved": True}, {"available": True}, {"parkingId": parking_id}]}))


def get_parking_image_queue():
    return list(parking_image_collection.find({}))


def remove_from_image_queue(parking_image):
    parking_image_collection.delete_one({"$and": [{"_id": parking_image['_id']}, {"creationDate": parking_image["creationDate"]}]})


def create_parking_spot(x1, y1, x2, y2,parking_id):
    spot = {
        "x1": x1,
        "y1": y1,
        "x2": x2,
        "y2": y2,
        "verificationCount": 0,
        "available": False,
        "approved": False,
        "lastUpdate": datetime.now(),
        "parkingId": parking_id
    }
    spot_collection.insert_one(spot)

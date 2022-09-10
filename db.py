from pymongo import MongoClient

Param = 10

client = MongoClient('mongodb://admin:fodfnoGUIYGb42d@45.83.123.118:27017/?authMechanism=DEFAULT')
spotCollection = client.get_database("parking_checker").get_collection("parking_spot")


def incVerificationCount(spot):
    if spot["verificationCount"] >= 19:
        spotCollection.update_one({"_id": spot['_id']}, {"$set": {"verificationCount": spot['verificationCount'] + 1,"approved" : True}})
    spotCollection.update_one({"_id": spot['_id']}, {"$set": {"verificationCount": spot['verificationCount'] + 1}})

def decVerificationCount(spot):
    if spot["verificationCount"] <= 0:
        spotCollection.update_one({"_id": spot['_id']}, {"$set": {"verificationCount": spot['verificationCount'] - 1,"approved" : False}})
    spotCollection.update_one({"_id": spot['_id']}, {"$set": {"verificationCount": spot['verificationCount'] - 1}})

def getSpots():
    return spotCollection.find({})


def createParking(x1, y1, x2, y2):
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

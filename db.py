from pymongo import MongoClient

Param = 10

client = MongoClient('mongodb://admin:fodffdsfgnoGUIYGb42d@45.83.123.118:27017/?authMechanism=DEFAULT')
spotCollection = client.get_database("parking_checker").get_collection("parking_spot")


def incVerificationCount(spot):
    if spot["verificationCount"] >= 19:
        spotCollection.update_one({"_id": spot['_id']}, {"$set": {"verificationCount": spot['verificationCount'] + 1,"approved" : True}})
    else:
        spotCollection.update_one({"_id": spot['_id']}, {"$set": {"verificationCount": spot['verificationCount'] + 1}})

def decVerificationCount(spot):
    if spot["verificationCount"] <= 0:
        spotCollection.delete_one({"_id": spot['_id']})
    else:
        spotCollection.update_one({"_id": spot['_id']}, {"$set": {"verificationCount": spot['verificationCount'] - 1}})

def getSpots():
    return list(spotCollection.find({}))

def getApprovedSpots():
    return list(spotCollection.find({"approved": True}))

def getAvailableApprovedSpots():
    return list(spotCollection.find({"$and":[{"approved": True},{"available": True}]}))
def createParking(x1, y1, x2, y2):
    spot = {
        "x1": x1,
        "y1": y1,
        "x2": x2,
        "y2": y2,
        "verificationCount": 0,
        "available": False,
        "approved": True
    }
    spotCollection.insert_one(spot)
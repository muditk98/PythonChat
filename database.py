import pymongo

mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")

db = mongo_client['chatap']

message_collection = 

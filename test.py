from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["data_db"]
collection = db["sensor_data"]

collection.insert_many([
    {"value": 10},
    {"value": 15},
    {"value": 100},  
    {"value": 12},
    {"value": 14},
    {"value": 200},
])

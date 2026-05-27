from pymongo import MongoClient
import json

client = MongoClient("mongodb://localhost:27017/")

db = client["dell_store"]

collection = db["products"]

with open("dell.json", "r", encoding="utf-8") as f:
    data = json.load(f)

products = data

if products:

    collection.insert_many(products)

    print(f"{len(products)} PRODUCTS INSERTED")

else:

    print("NO DATA FOUND")

print("\nFIRST PRODUCT:\n")

print(collection.find_one())
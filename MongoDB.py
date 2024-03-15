from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)


def DBinsert(
    request,
    collection,
    MessageID,
):
    db = client["Mails"]
    collection = db[collection]
    document = collection.find_one({"_id": MessageID})
    if document:
        collection.delete_one({"_id": MessageID})
        print(f"Document with ID {MessageID} deleted because of duplication.")
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {"_id": MessageID, "time": current_time, "text": request}
    collection.insert_one(data)
    print(f"{MessageID} Data inserted successfully!")

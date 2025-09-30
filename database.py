from motor.motor_asyncio import AsyncIOMotorClient
# This line imports the special tool, Motor, that lets your app talk to the MongoDB database without waiting for a response, keeping everything running smoothly.

MONGO_DETAILS = "mongodb://localhost:27017"
# This is the address of your local database.
# It's like a phone number, telling your app exactly where to find the MongoDB server running on your computer.

client = AsyncIOMotorClient(MONGO_DETAILS)
# This line uses Motor to establish a connection to the database server.

database = client.translator_db
# This selects a database to work with.
# If a database with this name doesn't exist, MongoDB will create it automatically when you first save data.

collection = database.translations
# This selects a collection within the database. 
# A collection is like a folder that holds all your translated documents. 
# This is where your data will be stored.

import asyncio

async def init_indexes():
    await collection.create_index("user_data.email", unique=False)

def get_database():
    return database
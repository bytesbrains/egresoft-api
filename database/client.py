from pymongo import MongoClient
import os

from dotenv import load_dotenv

load_dotenv()

db_client = MongoClient(os.getenv("MONGOCONNECT")).test

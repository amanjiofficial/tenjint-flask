from pymongo import MongoClient
from config import api_configuration

api_config = api_configuration()
client = MongoClient(api_config["api_database"])
db = client[api_config["api_database_name"]]

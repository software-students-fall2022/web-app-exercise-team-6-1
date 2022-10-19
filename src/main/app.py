import pymongo # import the module

from dotenv import dotenv_var

# make a connection to the database server
connection = pymongo.MongoClient("your_db_host", 27017,
                                username="your_db_username",
                                password="your_db_password",
                                authSource="your_db_name")
# select a specific database on the server
db = connection["your_db_name"]

connection = pymongo.MongoClient('mongodb://localhost:27017')
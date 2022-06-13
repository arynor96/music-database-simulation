import pymongo
from flask import Flask
import mysql.connector

app = Flask(__name__)

sql_config = {'user': 'user', 'password': 'password', 'host': 'sql', 'port': '3306', 'database': 'imse_m2_db'}
db = mysql.connector.connect(**sql_config)


mongo_client = pymongo.MongoClient('mongodb://user:password@mongo:27017')
mongo_db = mongo_client['imse_m2_mongo']


@app.route('/')
def hello_world():
    return 'Flask, MySQL, MongoDB and Docker are running'

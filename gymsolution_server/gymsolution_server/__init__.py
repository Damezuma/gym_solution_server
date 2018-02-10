"""
The flask application package.
"""
import pymysql
from flask import Flask
app = Flask(__name__)
connection = pymysql.connect(host="localhost",
                             user="test",
                             password="456456",
                             db="gym_db",
                             charset="utf8mb4",
                             cursorclass=pymysql.cursors.DictCursor
                             )
import gymsolution_server.views
import gymsolution_server.models
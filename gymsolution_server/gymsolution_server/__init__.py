"""
The flask application package.
"""
import pymysql
from flask import Flask, g

def get_conection():
    return pymysql.connect(host="localhost",
                             user="test",
                             password="456456",
                             db="gym_db",
                             charset="utf8mb4",
                             cursorclass=pymysql.cursors.DictCursor
                             )

app = Flask(__name__)
@app.before_request
def before_request():
    g.connection = get_conection()
@app.teardown_request
def teardown_request(exception):
    if hasattr(g, "connection"):
        g.connection.close()
import gymsolution_server.views
import gymsolution_server.models
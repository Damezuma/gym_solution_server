"""
The flask application package.
"""
import pymysql
from flask import Flask, g, Response
from datetime import time
class RuntimeError(Exception):
    def __init__(self, msg, code):
        self.message = msg
        self.code = code
    def to_response(self):
        d = {"msg": self.message}
        r = Response(response= json.dumps(d, default=json_handler), status=self.code, mimetype="application/json")
        return r
def json_handler(obj):
    if hasattr(obj,"__dict__"):
        return obj.__dict__
    elif type(obj) is set:
        return list(x for x in obj)
    elif type(obj) is time:
        return obj.strftime("%H:%M")
    else:
        return str(obj)

def get_conection():
    return pymysql.connect(host="localhost",
                             user="test",
                             password="456456",
                             db="gym_db",
                             charset="utf8mb4",
                             cursorclass=pymysql.cursors.DictCursor
                             )

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "/var/www/gymsolution_server/gymsolution_server"
@app.before_request
def before_request():
    g.connection = get_conection()
@app.teardown_request
def teardown_request(exception):
    if hasattr(g, "connection"):
        g.connection.close()
import gymsolution_server.views
import gymsolution_server.models


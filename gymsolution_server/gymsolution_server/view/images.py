from datetime import datetime,time
from flask import render_template, views, request, send_file, send_from_directory
from flask import Response
from gymsolution_server import app
import gymsolution_server.models as models
import json
from gymsolution_server import json_handler

@app.route("/images/<string:name>", methods=["GET"])
def images_get(name):
    return send_from_directory(app.config['UPLOAD_FOLDER'] +"/images", name)

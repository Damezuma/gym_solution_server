from datetime import datetime,time
from flask import render_template, views, request, send_file, send_from_directory
from flask import Response
from gymsolution_server import app
import gymsolution_server.models as models
import json
from gymsolution_server import json_handler, RuntimeError
@app.route("/gyms", methods=["GET"])
def clubs_get():
    response = dict()
    (response["msg"], status) = ("완료되었습니다", 200)
    r = models.Gym.list()
    response["result"] = r
    r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
    return r
@app.route("/gyms/<int:uid>/groups" , methods=["GET"])
def gym_groups_get(uid):
    response = dict()
    (response["msg"], status) = ("완료되었습니다", 200)
    token = request.headers.get("x-gs-token")
    if token is None:
        (response["msg"], status) = ("토큰이 존재하지 않습니다.", 403)
    elif type(models.User.get_by_token(token)) is models.NotFoundAccount:
         (response["msg"], status) = ("토큰이 유효하지 않습니다.", 403)
    else:
        r = models.Gym.find(uid)
        if r is None:
            (response["msg"], status) = ("해당하는 피트니스 클럽이 존재하지 않습니다.", 404)
        else:
            response["groups"] = r.get_groups()
    r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
    return r
@app.route("/gyms" , methods=["POST"])
def gym_post():
    response = dict()
    (response["msg"], status) = ("완료되었습니다", 200)
    data = None
    content_type = request.headers.get("content-type","")
    b = content_type.split(";")
    if b[0].find("json") != -1:
        data = request.data
        data = json.loads(data.decode("utf-8"))
    else:
        data = request.form
    name = data["name"]
    address = data["address"]
    latitude = data["latitude"]
    longitude = data["longitude"]
    r = models.Gym(None, latitude, longitude, name, address)
    if not r.insert():
        (response["msg"], status) = ("디비 쿼리에 실패했습니다.", 500)
    r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
    return r
@app.route("/gyms/<int:uid>" , methods=["DELETE"])
def gym_del(uid):
    response = dict()
    status = 200
    (response["msg"], status) = ("완료되었습니다", 200)
    
    r = models.Gym.find(uid)
    if r is None:
         (response["msg"], status) = ("해당하는 피트니스 클럽이 존재하지 않습니다.", 404)
    elif not r.delete():
        (response["msg"], status) = ("디비 쿼리에 실패했습니다.", 500)
    r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
    return r
@app.route("/gyms/<int:uid>/trainers")
def gym_trainer_get(uid):
    content_type = request.headers.get("content-type","")
    token = request.headers.get("x-gs-token")
    response = dict()
    (response["msg"], status) = ("완료되었습니다", 200)
    user = None
    if token is None:
        (response["msg"], status) = ("토큰이 존재하지 않습니다.", 403)
    else:
        user = models.User.get_by_token(token)
        if type(user) is models.NotFoundAccount:
            (response["msg"], status) = ("토큰이 유효하지 않습니다.", 403)
    if status != 200:
        r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
        return r
    gym = models.Gym(uid, None,None,None,None)
    response["trainers"] = gym.get_trainers()
    r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
    return r
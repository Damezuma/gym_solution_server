from datetime import datetime,time
from flask import render_template, views, request, send_file, send_from_directory
from flask import Response
from gymsolution_server import app
import gymsolution_server.models as models
import json



@app.route("/trainers/<int:uid>/groups", methods=["GET"])
def trainers_group_get(uid):
    response = dict()
    (response["msg"], status) = ("완료되었습니다", 200)
    token = request.headers.get("x-gs-token", None)
    if token is None:
        (response["msg"], status) = ("토큰이 존재하지 않습니다.", 403)
    else:
        r = models.User.get_by_token(token)
        if type(r) == models.NotFoundAccount:
             (response["msg"], status) = ("토큰이 유효하지 않습니다.", 403)
        else:
            r = models.Trainer(uid, None, None)
            response["groups"] = res
    #TODO:
    r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
    return r
@app.route("/trainer/<string:property_name>", methods=["PUT"])
def trainer_profileimage_put(property_name):
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
        elif type(user) is not models.Trainer:
            (response["msg"], status) = ("해당 기능은 트레이너만 이용할 수 있습니다.", 403)
    if status != 200:
        r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
        return r
    #user.update(self_introduction_text = request.data.decode("utf-8"))
    user.update(**{property_name: request.data.decode("utf-8")})
    r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
    return r


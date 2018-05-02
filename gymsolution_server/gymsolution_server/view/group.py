from datetime import datetime,time
from flask import render_template, views, request, send_file, send_from_directory
from flask import Response
from gymsolution_server import app
import gymsolution_server.models as models
import json

@app.route("/groups", methods=["POST"])
def groups_post():
    token = request.headers.get("x-gs-token")
    response = dict()
    status = 200
    (response["msg"], status) = ("완료되었습니다", 200)
    trainer = None
    if token is None:
        (response["msg"], status) = ("토큰이 존재하지 않습니다.", 403)
    else:
        temp = models.User.get_by_token(token)
        t = type(temp)
        if t is models.NotFoundAccount:
            (response["msg"], status) = ("토큰이 유효하지 않습니다.", 403)
        elif t is not models.Trainer:
             (response["msg"], status) = ("트레이너가 아닙니다.", 403)
        else:
            trainer = temp
    if trainer is None:
        r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
        return r
    data = None
    content_type = request.headers.get("content-type","")
    b = content_type.split(";")
    if b[0].find("json") != -1:
        data = request.data
        data = json.loads(data.decode("utf-8"))
    else:
        data = request.form
    
    capacity         = data.get("capacity", None)
    comment      = data.get("comment", None)
    _time               = data.get("time",None)
    charge          = data.get("charge",None)
    daysOfWeek= data.get("daysOfWeek",None)
    period = data.get("period",None)
    title = data.get("title", None)
    start_date = data.get("start_date", None)
    if capacity is None:
        (response["msg"], status) = ("capacity이(가) 들어오지 않았습니다.", 400)
    elif comment is None:    
        (response["msg"], status) = ("comment이(가) 들어오지 않았습니다.", 400)
    elif _time is None:
        (response["msg"], status) = ("time이(가) 들어오지 않았습니다.", 400)
    elif charge is None:
        (response["msg"], status) = ("charge이(가) 들어오지 않았습니다.", 400)
    elif daysOfWeek is None:
        (response["msg"], status) = ("daysOfWeek이(가) 들어오지 않았습니다.", 400)
    elif title is None:
        (response["msg"], status) = ("title이(가) 들어오지 않았습니다.", 400)
    elif period is None:
        (response["msg"], status) = ("period이(가) 들어오지 않았습니다.", 400)
    elif start_date is None:
        (response["msg"], status) = ("start_date이(가) 들어오지 않았습니다.", 400)
    if status != 200:
        r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
        return r
    if type(daysOfWeek) is list:
        daysOfWeek =("{}," * len(daysOfWeek)).format(*daysOfWeek)[:-1]
    t = None
    try:
        t = _time.split(":")
        t = list(int(x) for x in t)
        t = time(t[0], t[1])
    except:
        (response["msg"], status) = ("time이 잘못들어왔습니다. time은 hour:minute형식으로 들어와야 합니다. 보낸 데이터는 {}입니다.".format(_time), 400)
        r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
        return r
    _time = t
    gym = models.Gym.find(trainer.gym_uid)
    group = models.Group(None,gym,"Y",trainer, capacity,comment, _time,charge, daysOfWeek,start_date,period , title)
    if not group.insert():
        (response["msg"], status) = ("DB에러가 났습니다.", 500)
    r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
    return r
@app.route("/groups",  methods = ["GET"])
def grouplist_get():
    response = dict()
    status = 200
    (response["msg"], status) = ("완료되었습니다", 200)
    lat = request.args.get("lat", None)
    long = request.args.get("long",None)
    rad = request.args.get("rad", None)
    token = request.headers.get("x-gs-token")
    if token is None:
        (response["msg"], status) = ("토큰이 존재하지 않습니다.", 403)
    else:
        t = type(models.User.get_by_token(token))
        if t is models.NotFoundAccount:
            (response["msg"], status) = ("토큰이 유효하지 않습니다.", 403)
    if status != 200:
        r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
        return r
    response["groups"] = models.Group.get_list(lat, long, rad)
    r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
    return r
@app.route("/groups/<int:group_uid>/users/<int:trainee_uid>/bodymeasurements", methods=["POST"])
def groups_GROUPUID_users_TRAINEE_UID_bodymeasurements_post(group_uid, trainee_uid):
#TODO: 기존 코드를 기반으로 구현해야 함, 아래 코드는 아직 구현된 것이 아님
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
    form = request.data
    form = json.loads(form.decode("utf-8"))
    print(form)
    img = form.get("img", None)
    image_name = None
    weight = form.get("weight", None)
    muscle = form.get("muscle", None)
    fat = form.get("fat", None)
    comment = form.get("comment", None)
    img_type = None
    if img is not None:
        import base64
        import hashlib
        hash512 = hashlib.sha512()
        img_type =str(img["type"])
        img = base64.decodebytes(img["data"].encode())
        
        hash512.update(img)
        image_name = hash512.hexdigest()
    
    measurement_log = models.MeasurementInfo(image_name, user, img, img_type, weight, muscle, fat)
    measurement_log.upload()
    r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
    return r
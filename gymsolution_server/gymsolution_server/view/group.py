from datetime import datetime,time
from flask import render_template, views, request, send_file, send_from_directory
from flask import Response
from gymsolution_server import app
import gymsolution_server.models as models
import json
from gymsolution_server import json_handler, RuntimeError




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
    response = dict()
    try:
        content_type = request.headers.get("content-type","")
        token = request.headers.get("x-gs-token")
        (response["msg"], status) = ("완료되었습니다", 200)
        user = None
        if token is None:
            raise RuntimeError("토큰이 존재하지 않습니다.", 403)
        else:
            user = models.User.get_by_token(token)
            if type(user) is models.NotFoundAccount:
                raise RuntimeError("토큰이 유효하지 않습니다.", 403)
                
        if status != 200:
            r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
            return r
        #토큰이 올바른 지 확인했다면, 이제 이 토큰이 해당 그룹의 개설자인지 확인해야 함
        group = models.Group.find(group_uid)
        if group is None:
            raise RuntimeError("그룹이 유효하지 않습니다.", 403)
        if group.opener.uid != user.uid:
            raise RuntimeError("그룹의 개설자가 아닙니다.", 403)
        #TODO: 날짜까지 반영해야 함
        trainee = models.User.find(trainee_uid)
        if type(trainee) is not models.Trainee:
            raise RuntimeError("유저가 잘못되었습니다.", 403)
        if not group in trainee.get_groups():
            raise RuntimeError("해당 그룹에 유저가 가입하지 않았습니다.", 403)
        form = request.data
        form = json.loads(form.decode("utf-8"))
        print(form)
        img = form.get("img", None)
        d =  form.get("date", None)
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
    
        measurement_log = models.MeasurementInfo(image_name, user,trainee, img, img_type, weight, muscle, fat, comment)
        measurement_log.upload()
    except  RuntimeError as e:
        return e.to_response()
    r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
    return r
@app.route("/groups/<int:uid>", methods=["GET"])
def groups_UID_get(uid):
    response = dict()
    try:
        token = request.headers.get("x-gs-token", None)
        if token is None:
           raise RuntimeError("토큰이 존재하지 않습니다.", 403)
        if type(models.User.get_by_token(token)) is models.NotFoundAccount:
           raise RuntimeError ("토큰이 유효하지 않습니다.", 403)
        group = models.Group.find(uid)
        if group is None:
            raise RuntimeError ("그룹이 존재하지 않습니다.", 404)
        response = group
    except RuntimeError as  e:
        return e.to_response()
    r = Response(response= json.dumps(response, default=json_handler), status=200, mimetype="application/json")
    return r
    
@app.route("/groups/<int:uid>/users/<int:trainee>/bodymeasurements", methods=["GET"])
def groups_UID_users_TRAINEE_bodymeasurements_get(uid, trainee):
    response = dict()
    try:
        content_type = request.headers.get("content-type","")
        token = request.headers.get("x-gs-token")
        (response["msg"], status) = ("완료되었습니다", 200)
        user = None
        if token is None:
            raise RuntimeError("토큰이 존재하지 않습니다.", 403)
        else:
            user = models.User.get_by_token(token)
            if type(user) is models.NotFoundAccount:
                raise RuntimeError("토큰이 유효하지 않습니다.", 403)
        group = models.Group.find(uid)
        if group is None:
            raise RuntimeError("그룹이 유효하지 않습니다.", 403)
        if group.opener.uid != user.uid:
            raise RuntimeError("그룹의 개설자가 아닙니다.", 403)
        trainee = models.User.find(trainee)
        if type(trainee) is not models.Trainee:
            raise RuntimeError("유저가 잘못되었습니다.", 403)
        if not group in trainee.get_groups():
            raise RuntimeError("해당 그룹에 유저가 가입하지 않았습니다.", 403)
        response = models.MeasurementInfoList.get(trainee)
    except RuntimeError as e:
        return e.to_response()

    r = Response(response= json.dumps(response, default=json_handler), status=200, mimetype="application/json")
    return r
@app.route("/groups/<int:uid>/trainings/<udate>", methods=["PUT"])
def groups_UID_trainings_UDATE_post(uid,udate):
    response = dict()
    try:
        content_type = request.headers.get("content-type","")
        token = request.headers.get("x-gs-token")
        (response["msg"], status) = ("완료되었습니다", 200)
        user = None
        if token is None:
            raise RuntimeError("토큰이 존재하지 않습니다.", 403)
        else:
            user = models.User.get_by_token(token)
            if type(user) is models.NotFoundAccount:
                raise RuntimeError("토큰이 유효하지 않습니다.", 403)
        group = models.Group.find(uid)
        if group is None:
            raise RuntimeError("그룹이 유효하지 않습니다.", 403)
        if group.opener.uid != user.uid:
            raise RuntimeError("그룹의 개설자가 아닙니다.", 403)
        form = request.data
        form = json.loads(form.decode("utf-8"))
        if len(form) > 6:
            raise RuntimeError("등록할 운동 갯수가 6개를 초과합니다.", 403)
        err_m = list()
        fields = {"name", "count", "set"}
        for idx, training in enumerate(form):
            for field in fields:
                if training.get(field) is None:
                    err_m.append("{}번째 운동 기록에 {}이(가) 누락되었습니다.".format(idx, field))
        def filter_training(training):
            fields = {"name", "count", "set"}
            for field in fields:
                if training.get(field) is None:
                    return False
            return True

        trainings = (models.Training(i, udate, group, form[i]["name"], form[i]["count"], form[i]["set"]) for i in range(len(form)))
        for t in map(lambda it:models.Training(it[0], udate, group, it[1]["name"], it[1]["count"], it[1]["set"]) ,enumerate(filter(filter_training, form))):
            t.insert()
        from flask import g
        connection = g.connection
        connection.commit()
        response["msg"] = "완료되었습니다."
    except RuntimeError as e:
        return e.to_response()
    r = Response(response= json.dumps(response, default=json_handler), status=200, mimetype="application/json")
    return r
@app.route("/groups/<int:uid>/trainings", methods=["GET"])
def groups_UID_trainings_get(uid):
    response = dict()
    try:
        content_type = request.headers.get("content-type","")
        token = request.headers.get("x-gs-token")
        (response["msg"], status) = ("완료되었습니다", 200)
        user = None
        if token is None:
            raise RuntimeError("토큰이 존재하지 않습니다.", 403)
        else:
            user = models.User.get_by_token(token)
            if type(user) is models.NotFoundAccount:
                raise RuntimeError("토큰이 유효하지 않습니다.", 403)
        group = models.Group.find(uid)
        if group is None:
            raise RuntimeError("그룹이 유효하지 않습니다.", 403)

        response = models.Training.get_list(group)

    except RuntimeError as e:
        return e.to_response()
    r = Response(response= json.dumps(response, default=json_handler), status=200, mimetype="application/json")
    return r

@app.route("/groups/<int:uid>/users/<int:u_uid>/results/before")
def groups_UID_users_UUID_results_before_get(uid, u_uid):
    response = dict()
    try:
        content_type = request.headers.get("content-type","")
        token = request.headers.get("x-gs-token")
        (response["msg"], status) = ("완료되었습니다", 200)
        user = None
        if token is None:
            raise RuntimeError("토큰이 존재하지 않습니다.", 403)
        else:
            user = models.User.get_by_token(token)
            if type(user) is models.NotFoundAccount:
                raise RuntimeError("토큰이 유효하지 않습니다.", 403)
        group = models.Group.find(uid)
        if group is None:
            raise RuntimeError("그룹이 유효하지 않습니다.", 403)
        trainee = models.User.find(u_uid)
        if type(trainee) is not models.Trainee:
            raise RuntimeError("유저가 잘못되었습니다.", 403)
        if not group in trainee.get_groups():
            raise RuntimeError("해당 그룹에 유저가 가입하지 않았습니다.", 403)
        response = models.MeasurementInfoList.get_before(group, trainee)
    except RuntimeError as e:
        return e.to_response()

    r = Response(response= json.dumps(response, default=json_handler), status=200, mimetype="application/json")
    return r
@app.route("/groups/<int:uid>/users/<int:u_uid>/results/after")
def groups_UID_users_UUID_results_after_get(uid, u_uid):
    response = dict()
    try:
        content_type = request.headers.get("content-type","")
        token = request.headers.get("x-gs-token")
        (response["msg"], status) = ("완료되었습니다", 200)
        user = None
        if token is None:
            raise RuntimeError("토큰이 존재하지 않습니다.", 403)
        else:
            user = models.User.get_by_token(token)
            if type(user) is models.NotFoundAccount:
                raise RuntimeError("토큰이 유효하지 않습니다.", 403)
        group = models.Group.find(uid)
        if group is None:
            raise RuntimeError("그룹이 유효하지 않습니다.", 403)
        trainee = models.User.find(u_uid)
        if type(trainee) is not models.Trainee:
            raise RuntimeError("유저가 잘못되었습니다.", 403)
        if not group in trainee.get_groups():
            raise RuntimeError("해당 그룹에 유저가 가입하지 않았습니다.", 403)
        response = models.MeasurementInfoList.get_after(group, trainee)
    except RuntimeError as e:
        return e.to_response()

    r = Response(response= json.dumps(response, default=json_handler), status=200, mimetype="application/json")
    return r
@app.route("/groups/<int:uid>/users")
def groups_UID_users_get(uid):
    response = dict()
    try:
        content_type = request.headers.get("content-type","")
        token = request.headers.get("x-gs-token")
        (response["msg"], status) = ("완료되었습니다", 200)
        user = None
        if token is None:
            raise RuntimeError("토큰이 존재하지 않습니다.", 403)
        else:
            user = models.User.get_by_token(token)
            if type(user) is models.NotFoundAccount:
                raise RuntimeError("토큰이 유효하지 않습니다.", 403)
        group = models.Group.find(uid)
        if group is None:
            raise RuntimeError("그룹이 유효하지 않습니다.", 403)
        response = group.get_members()

    except RuntimeError as e:
        return e.to_response()
    r = Response(response= json.dumps(response, default=json_handler), status=200, mimetype="application/json")
    return r
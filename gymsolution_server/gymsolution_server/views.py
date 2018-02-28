"""
Routes and views for the flask application.
"""
from datetime import datetime,time
from flask import render_template, views, request
from flask import Response
from gymsolution_server import app
import gymsolution_server.models as models
import json
def json_handler(obj):
    if hasattr(obj,"__dict__"):
        return obj.__dict__
    else:
        return str(obj)

@app.route("/users", methods=["POST"])
def users_post():
    
    content_type = request.headers.get("content-type","")
    name = None
    password = None
    phonenumber = None
    type = None
    fitness_club_idx = None
    gender = None
    birthday = None
    data = None
    print(content_type)
    b = content_type.split(";")
    if b[0].find("json"):
        data = request.data
        data = json.loads(data.decode("utf-8"))
    else:
        data = request.form
    name = data.get("name")
    password = data.get("password")
    phonenumber = data.get("phonenumber")
    type = data.get("type")
    fitness_club_idx = data.get("fitness_club_idx")
    gender = data.get("gender")
    birthday = data.get("birthday")
    user = None
    response = dict()
    status, response["msg"] = (200 , "완료되었습니다")
   
    if name is None:
        status, response["msg"] = (400 , "'name'이(가) 누락되었습니다.")
    elif password is None:
        status, response["msg"] = (400 , "'password'이(가) 누락되었습니다.")
    elif len(password.strip()) < 6:
        status, response["msg"] = (400 , "'password'이(가) 잘못되었습니다.")
    elif phonenumber is None:
        status, response["msg"] = (400 , "'phonenumber'이(가) 누락되었습니다.")
    elif phonenumber.find("-") != -1 or len(phonenumber) != 11:
        status, response["msg"] = (400 , "'phonenumber'이(가) 잘못되었습니다.")
    elif type is None:
        status, response["msg"] = (400 , "'type'이(가) 누락되었습니다")
    elif type == "trainee":
        if gender is None:
            status, response["msg"] = (400 , "'gender'이(가) 누락되었습니다.")
        elif birthday is None:
            status, response["msg"] = (400 , "'birthday'이(가) 누락되었습니다.")
        else:
            user = models.Trainee()
            user.gender = gender
            user.birthday = birthday
    elif type == "trainer":
        if fitness_club_idx is None:
            status, response["msg"] = (400 , "'fitness_club_idx'이(가) 누락되었습니다.")
        else:
            user = models.Trainer()
            user.gym_uid = int(fitness_club_idx)
    else:
        status, response["msg"] = (400 , "'type'이(가) 누락되었습니다.")
    if user is not None:
        user.name = name
        user.phonenumber = phonenumber
        user.password = password.strip()
        if user.insert() == False:
            status , response["msg"] = (400, "전화번호가 중복됩니다")
    if status != 200:
        data = request.data
        response["body"] = data.decode("utf-8")
        print(response["body"])
    r = Response(response= json.dumps(response), status=status, mimetype="application/json")
    
    r.headers["Content-Type"] = "application/json; charset=utf-8"
    return r
@app.route("/users", methods=["GET"])
def users_get():
    trainees = models.Trainee.list()
    import json
    
    text = json.dumps(trainees, default=lambda o : o.__dict__)
    r = Response(response=text, status=200, mimetype="application/json")
    r.headers["Content-Type"] = "application/json; charset=utf-8"
    return r
@app.route("/token", methods=["GET"])
def token_get():
    response = dict()
    (response["msg"], status) = ("완료되었습니다", 200)

    id = request.headers.get("x-gs-id")
    password = request.headers.get("x-gs-password")
    if id is None:
         (response["msg"], status) = ("id가 들어오지 않았습니다.", 400)
    if password is None:
         (response["msg"], status) = ("password가 들어오지 않았습니다.", 400)
    if status != 200:
        r = Response(response= json.dumps(response), status=status, mimetype="application/json")
        return r
    
    #user_client = request.headers.get("user-agent")
    user = models.User()
    user.phonenumber = id
    user.password = password
    r = user.check_permission()
    r_t = type(r)
    if r_t == models.NotFoundAccount:
        (response["msg"], status) = (r.error_msg, 404)
    elif r_t == models.IncollectPassword:
        (response["msg"], status) = (r.error_msg, 400)
    else:
        import hashlib
        import datetime
        hash = hashlib.sha512()
        d = datetime.datetime.now()
        d = d.strftime("%Y-%m-%d %H:%M:%S")
        token = "{} {}".format(d, user.phonenumber);
        hash.update(token.encode())
        token = hash.hexdigest()
        r.update_token(token)
        response["token"] = token

    r = Response(response= json.dumps(response), status=status, mimetype="application/json")
    return r
@app.route("/tokens/<string:token>/user", methods=["GET"])
def token_user_get(token:str):
    response = dict()
    (response["msg"], status) = ("완료되었습니다", 200)
    r = models.User.get_by_token(token)
    if type(r) == models.NotFoundAccount:
         (response["msg"], status) = ("토큰이 유효하지 않습니다.", 403)
    else:
        response["user"] = r
    r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
    return r
@app.route("/tokens/<string:token>/user/groups", methods=["GET"])
def token_user_group_get(token:str):
    response = dict()
    (response["msg"], status) = ("완료되었습니다", 200)
    r = models.User.get_by_token(token)
    if type(r) == models.NotFoundAccount:
         (response["msg"], status) = ("토큰이 유효하지 않습니다.", 403)
    else:
        res = r.get_entered_groups()
        response["groups"] = res
    #TODO:
    r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
    return r
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
    if status != 200:
        r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
        return r
    if type(daysOfWeek) is list:
        daysOfWeek =("{}," * len(daysOfWeek)).format(*daysOfWeek)[:-1]
    _time = _time.split(":")
    _time = list(int(x) for x in _time)
    _time = time(_time[0], _time[1])
    gym = models.Gym.find(trainer.gym_uid)
    group = models.Group(None,gym,"Y",trainer, capacity,comment, _time,charge, daysOfWeek,None,None )
    if not group.insert():
        (response["msg"], status) = ("DB에러가 났습니다.", 500)
    r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
    return r
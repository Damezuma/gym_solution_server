from datetime import datetime,time
from flask import render_template, views, request, send_file, send_from_directory
from flask import Response
from gymsolution_server import app
import gymsolution_server.models as models
import json
from gymsolution_server import json_handler
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
    print(data)
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
            user = models.Trainee(None,None,None,None)
            user.gender = gender
            user.birthday = birthday
    elif type == "trainer":
        if fitness_club_idx is None:
            status, response["msg"] = (400 , "'fitness_club_idx'이(가) 누락되었습니다.")
        else:
            user = models.Trainer(0, None, None, None)
            user.gym_uid = int(fitness_club_idx)
    else:
        status, response["msg"] = (400 , "'type'이(가) 누락되었습니다.")
    if user is not None:
        user.name = name
        user.phonenumber = phonenumber
        user.password = password.strip()
        if user.insert() == False:
            (status , response["msg"] )= (400, "전화번호가 중복됩니다")
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
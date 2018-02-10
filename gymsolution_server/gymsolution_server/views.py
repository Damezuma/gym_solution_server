"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, views, request
from flask import Response
from gymsolution_server import app
import gymsolution_server.models as models
import json
@app.route("/users", methods=["POST"])
def users_post():
    name = request.form.get("name")
    password = request.form.get("password")
    phonenumber = request.form.get("phonenumber")
    type = request.form.get("type")
    fitness_club_idx = request.form.get("fitness_club_idx")
    gender = request.form.get("gender")
    birthday = request.form.get("birthday")
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
    id = request.headers.get("x-gs-id")
    password = request.headers.get("x-gs-password")
    #user_client = request.headers.get("user-agent")
    user = models.User()
    user.phonenumber = id
    user.password = password
    r = user.check_permission()
    response = dict()
    (response["msg"], status) = ("완료되었습니다", 200)
    if r is None:
        (response["msg"], status) = ("완료되었습니다", 200)
        
    return json.dumps(response), status
@app.route("/clubs", methods=["GET"])
def clubs_get():
    return "OK", 200

    
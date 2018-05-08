from datetime import datetime,time
from flask import render_template, views, request, send_file, send_from_directory
from flask import Response
from gymsolution_server import app
import gymsolution_server.models as models
import json
from gymsolution_server import json_handler
@app.route("/user", methods=["GET"])
def token_user_get():
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
            response["user"] = r
    r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
    return r
@app.route("/user/groups", methods=["GET"])
def token_user_group_get():
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
            res = r.get_groups()
            response["groups"] = res

    r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
    return r
@app.route("/user/groups/<int:group>", methods=["PUT"])
def token_user_group_post(group):
    response = dict()
    status = 200
    (response["msg"], status) = ("완료되었습니다", 200)
    trainee = None
    token = request.headers.get("x-gs-token", None)
    if token is None:
        (response["msg"], status) = ("토큰이(가) 존재하지 않습니다.", 403)
    else:
        temp = models.User.get_by_token(token)
        t = type(temp)
        if t is models.NotFoundAccount:
            (response["msg"], status) = ("토큰이(가) 유효하지 않습니다.", 403)
        elif t is not models.Trainee:
             (response["msg"], status) = ("트레이니이(가) 아닙니다.", 403)
        else:
            trainee = temp
    if trainee is None:
        r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
        return r
    group = models.Group.find(group)
    if group is None:
         (response["msg"], status) = ("그룹이(가) 존재하지 않습니다.", 404)
    elif not group.opened:
        (response["msg"], status) = ("그룹 참가이(가) 마감되었습니다.", 404)
    else:
        res = trainee.enter_group(group)
        if not res:
            (response["msg"], status) = ("그룹에 들어갈 수 없습니다.", 404)
    r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
    return r

@app.route("/user/images", methods=["POST"])
def user_images_post():
    content_type = request.headers["Content-Type"]
    
    response = dict()
    (response["msg"], status) = ("완료되었습니다", 200)
    user = None
    token = request.headers.get("x-gs-token", None)
    if token is None:
        (response["msg"], status) = ("토큰이 존재하지 않습니다.", 403)
    else:
        user = models.User.get_by_token(token)
        if type(user) is models.NotFoundAccount:
            (response["msg"], status) = ("토큰이 유효하지 않습니다.", 403)
    if status != 200:
        r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
        return r
    content_type = request.headers["Content-Type"]
    encoding = content_type.split(";")[1].strip()
    content_type =list(it.strip() for it in  content_type.split(";")[0].strip().split("/"))
    if content_type[0] == "image":
        data = request.data
        if encoding == "base64":
            import base64
            data = base64.decodebytes(data)
        import hashlib
        hash512 = hashlib.sha512()
        hash512.update(data)
        filename = hash512.hexdigest()
        image = models.Image(filename,user, data, content_type[1] )
        image.upload()
        r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
        return r
@app.route("/user/images", methods=["GET"])
def user_images_get():
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
@app.route("/user/bodymeasurements",methods=["POST"])
def user_bodymeasurements_post():
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
    
    measurement_log = models.MeasurementInfo(
        image_name=image_name,
        uploader=user,
        data=img,
        image_type=img_type,
        weight=weight,
        muscle=muscle,
        fat=fat,
        comment=comment)
    measurement_log.upload()
    r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
    return r
@app.route("/user/bodymeasurements",methods=["GET"])
def user_bodymeasurements_get():
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
    response["list"] = models.MeasurementInfoList.get(user)
    r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
    return r
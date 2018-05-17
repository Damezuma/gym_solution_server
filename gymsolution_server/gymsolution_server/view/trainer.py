from datetime import datetime,time
from flask import render_template, views, request, send_file, send_from_directory
from flask import Response
from gymsolution_server import app
import gymsolution_server.models as models
import json
from gymsolution_server import json_handler, RuntimeError



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

@app.route("/trainers/<int:uid>/images", methods=["GET"])
def trainers_UID_images_get(uid):
    response = dict()
    try:
        token = request.headers.get("x-gs-token", None)
        if token is None:
            raise RuntimeError("토큰이 존재하지 않습니다.",400)
        user = models.User.get_by_token(token)
        if type(user) is models.NotFoundAccount:
            raise RuntimeError("토큰이 유효하지 않습니다.", 403)
        trainer = models.Trainer.find(uid)
        if type(trainer) is not models.Trainer:
            raise RuntimeError("해당 uid는 트레이너가 아닙니다.", 403)
        res =models.Image.get_list(trainer)
        for it in res:
            it.image_name = "https://gym.hehehee.net/images/{}".format(it.image_name)
        response["images"] = res
    except RuntimeError as e:
        return e.to_response()
    (response["msg"], status) = ("완료되었습니다", 200)
    r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
    return r
@app.route("/trainers/<int:uid>/images/<string:name>", methods=["DELETE"])
def trainers_UID_images_get(uid):
    response = dict()
    try:
        token = request.headers.get("x-gs-token", None)
        if token is None:
            raise RuntimeError("토큰이 존재하지 않습니다.",400)
        user = models.User.get_by_token(token)
        if type(user) is models.NotFoundAccount:
            raise RuntimeError("토큰이 유효하지 않습니다.", 403)
        trainer = models.Trainer.find(uid)
        if type(trainer) is not models.Trainer:
            raise RuntimeError("해당 uid는 트레이너가 아닙니다.", 403)
        res =models.Image.get_list(trainer)
        if not name in  (x.image_name for x in res):
            raise RuntimeError("이미지 파일이 존재하지 않습니다.", 403)
        img = models.Image(NameError, trainer)
        img.delete()
        response["images"] = res
    except RuntimeError as e:
        return e.to_response()
    (response["msg"], status) = ("완료되었습니다", 200)
    r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
    return r
@app.route("/trainers/<int:uid>/images", methods=["POST"])
def trainers_UID_images_post(uid):
    response = dict()
    try:
        token = request.headers.get("x-gs-token", None)
        if token is None:
            raise RuntimeError("토큰이 존재하지 않습니다.",400)
        user = models.User.get_by_token(token)
        if type(user) is not models.Trainer:
            raise RuntimeError("토큰이 유효하지 않습니다.", 403)
        trainer = models.Trainer.find(uid)
        if type(trainer) is not models.Trainer:
            raise RuntimeError("해당 uid는 트레이너가 아닙니다.", 403)
        if user.uid != trainer.uid:
            raise RuntimeError("업로드 권한이 없습니다.", 403)
        form = request.data
        form = json.loads(form.decode("utf-8"))
        img = form.get("data", None)
        content_type = request.headers.get("content-type")
        if img is None:
            raise RuntimeError("이미지가 없습니다.", 403)
        
        import base64
        import hashlib
        temp = content_type.split(";")
        mime = temp[0].split("/")[1].strip()
        b = temp[1].strip()
        hash512 = hashlib.sha512()
        img = base64.decodebytes(img.encode())
        hash512.update(img)
        image_name = hash512.hexdigest() + "." + mime
        res = models.Image(image_name, trainer, img,  None)
        res.upload()
        
    except RuntimeError as e:
        return e.to_response()
    (response["msg"], status) = ("완료되었습니다", 200)
    r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
    return r
@app.route("/trainers/<int:uid>/reviews", methods=["GET"])
def trainers_UID_reviews_get(uid:int):
    response = dict()
    response["msg"] = "완료되었습니다"
    status = 200
    try:
        token = request.headers.get("x-gs-token", None)
        if token is None:
            raise RuntimeError("토큰이 존재하지 않습니다.",400)
        user = models.User.get_by_token(token)
        if type(user)  is models.NotFoundAccount:
            raise RuntimeError("토큰이 유효하지 않습니다.", 403)
        trainer = models.Trainer.find(uid)
        if type(trainer) is not models.Trainer:
            raise RuntimeError("해당 uid는 트레이너가 아닙니다.", 403)
        res = models.Review.get_list(trainer)
        response["reviews"]  = res
    except RuntimeError as e:
        return e.to_response()
    r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
    return r
@app.route("/trainers/<int:uid>/reviews", methods=["POST"])
def trainers_UID_reviews_post(uid:int):
    response = dict()
    response["msg"] = "완료되었습니다"
    status = 200
    try:
        token = request.headers.get("x-gs-token", None)
        if token is None:
            raise RuntimeError("토큰이 존재하지 않습니다.",400)
        user = models.User.get_by_token(token)
        if type(user) is not models.Trainee:
            raise RuntimeError("토큰이 유효하지 않습니다.", 403)
        trainer = models.Trainer.find(uid)
        if type(trainer) is not models.Trainer:
            raise RuntimeError("해당 uid는 트레이너가 아닙니다.", 403)
        #해당 유저가 트레이너가 개최한 그룹에 속해 있어야 한다. 
        trainer_groups =  trainer.get_groups()
        user_groups = user.get_groups()
        if len( filter(lambda x: x in trainer_groups, user_groups)) ==0:
            raise RuntimeError("해당 유저는 트레이너를 리뷰할 수 없습니다.", 403)
        form = request.data
        form = json.loads(form.decode("utf-8"))
        
        comments = form.get("comments", None)
        grade = form.get("grade", None)
        
        if comments is None or grade is None:
            raise RuntimeError("리뷰를 제대로 전송하지 않았습니다.", 403)

        review = models.Review(None, trainer, user,comments,grade)
        review.insert()

    except RuntimeError as e:
        return e.to_response()
    r = Response(response= json.dumps(response, default=json_handler), status=status, mimetype="application/json")
    return r
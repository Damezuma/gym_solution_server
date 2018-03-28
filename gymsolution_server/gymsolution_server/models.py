from flask import g
from pymysql import Error
import datetime
from gymsolution_server import app
class Error:
    error_msg = ""
    def __init__(self, msg):
        self.error_msg = msg
        pass
class IncollectPassword(Error):
    def __init__(self):
        return super().__init__("password가 다릅니다.")
class NotFoundAccount(Error):
    def __init__(self):
        return super().__init__("계정을 찾을 수 없습니다.")
class User:
    uid = None
    name = None#str()
    password = None#str()
    phonenumber = None#str()

    def __init__(self, uid = None, phonenumber = None, name = None, password = None):
        self.uid = uid
        self.name = name
        self.phonenumber = phonenumber
        self.password = password
    @staticmethod
    def get_by_token(token:str):
        from flask import g
        connection = g.connection
        cur = connection.cursor()
        args = (token)
        cur.execute("SELECT * FROM token = %s",  args)
        connection.close()
        #TODO:
        return None
    @staticmethod
    def find(uid:int):
        from flask import g
        connection = g.connection
        cur = connection.cursor()
        args = (uid)
        cur.execute("SELECT * FROM  v_users WHERE uid = %s ",  args)
        row = cur.fetchone()
        if row is None:
            return None
        user = None
        _class = None
        param = dict()
        param["name"] = row["name"]
        param["uid"] = row["uid"]
        if row["gym_uid"] is None:
            param["gender"] = row["gender"]
            param["birthday"] = row["birthday"]
            _class = Trainee
        else:
            _class = Trainer
            param["gym_uid"] = row["gym_uid"]
        user = _class(**param)
        return user
    def check_permission(self):
        from flask import g
        connection = g.connection
        cur = connection.cursor()
        args = (self.password , self.phonenumber)
        cur.execute("SELECT password = password(%s) as `is_collect`, uid, name FROM tb_users WHERE phone_number = %s",  args)
        row = cur.fetchone()
        if row is None:
            return NotFoundAccount()
        if row["is_collect"] == False:
            return IncollectPassword()
        id = row["uid"]
        name = row["name"]
        args = (id)
        cur.execute("SELECT * FROM tb_trainees WHERE user_uid = %s",  args)
        row = cur.fetchone()
        if row is not None:
            gender = row["gender"]
            res = Trainee(int(id), name, gender, row["birthday"], self.phonenumber,None )
            cur.close()
            return res
        cur.execute("SELECT * FROM tb_trainers WHERE user_uid = %s",  args)
        row = cur.fetchone()

        if row is not None:
            res = Trainer(int(id),name,row["gym_uid"], self.phonenumber)
            cur.close()
            return res
        cur.close()
        return None
    def update_token(self, token):
        from flask import g
        connection = g.connection
        cur = connection.cursor()
        args = (token, self.uid )
        cur.execute("UPDATE tb_users SET token = %s WHERE uid = %s",  args)
        connection.commit()
        
        cur.close()
        pass
    @staticmethod
    def get_by_token(token):
        from flask import g
        connection = g.connection
        cur = connection.cursor()
        args = (token)
        cur.execute("SELECT * FROM  v_users WHERE token = %s ",  args)
        row = cur.fetchone()
        if row is None:
            return NotFoundAccount()
        user = None
        _class = None
        param = dict()
        param["name"] = row["name"]
        param["uid"] = row["uid"]
        if row["gym_uid"] is None:
            param["gender"] = row["gender"]
            param["birthday"] = row["birthday"]
            _class = Trainee
        else:
            _class = Trainer
            param["gym_uid"] = row["gym_uid"]
        user = _class(**param)
        return user
class Trainer(User):
    gym_uid = None#int()
    def __init__(self, uid:int,  name:str, gym_uid:int , phonenumber:str = None, password:str = None, token:str = None,):
        User.__init__(self, uid, phonenumber, name, password)
        self.gym_uid = gym_uid
        pass
    def insert(self):
        from flask import g
        connection = g.connection
        condition = False
        condition = condition or (self.gym_uid is None)
        condition = condition or (self.name is None)
        condition = condition or (self.password is None)
        condition = condition or (self.phonenumber is None)
        if condition:
            return False
        cur = connection.cursor()
        arg =  (self.phonenumber, self.name, self.password)
        cur.execute("INSERT INTO tb_users (phone_number, name, password) VALUES (%s, %s, password(%s))",arg)
        cur.execute("SELECT last_insert_id() as 'uid'")
        row = cur.fetchone()
        self.uid = row["uid"]
        arg = (self.uid, self.gym_uid)
        cur.execute("INSERT INTO tb_trainers (user_uid, gym_uid) VALUES (%s, %s)", arg)
        connection.commit()
        cur.close()
        return True
    
    def get_groups(self):
        from flask import g
        connection = g.connection
        cur = connection.cursor()
        args = (self.uid)
        cur.execute("SELECT * FROM tb_groups WHERE opener_uid = %s ",  args)
        res = list();
        row = cur.fetchone()
        while row is not None:
            group = dict()
            gym_uid = row["gym_uid"]
            opener_uid = row["opener_uid"]
            if  not gym_uid in  gyms:
                gyms[gym_uid] = Gym.find(gym_uid)
            if not opener_uid in openers:
                openers[opener_uid] = User.find(opener_uid)
            group["gym"] = gyms[gym_uid]
            group["opener"] = openers[opener_uid]
            group["uid"] = row["uid"]
            group["opened"] = row["opened"]
            
            group["capacity"] = row["capacity"]
            group["comment"] = row["comment"]
            group["time"] = row["time"]
            group["charge"] = row["charge"]
            group["daysOfWeek"] = DaysOfWeeks(row["uid"])
            group["start_date"] = row["start_date"]
            group["period"] = row["period"]
            group["title"] = row["title"]
            g = Group(**group)
            res.append(g)
            row = cur.fetchone()
        cur.close()
        return res
        #
class Trainee(User):
    gender = None#str()
    birthday = None#datetime.date.
    def __init__(self, uid:int,  name:str, gender:str ,birthday:datetime.date, phonenumber:str = None, password:str = None):
        User.__init__(self, uid, phonenumber, name, password)
        self.gender = gender
        self.birthday = birthday
        pass
    @staticmethod
    def list():
        from flask import g
        connection = g.connection
        cur = connection.cursor()
        cur.execute("SELECT * FROM v_trainees")
        res = list();
        row = cur.fetchone()
        while row is not None:
            trainee = Trainee()
            trainee.uid = row["uid"]
            trainee.name = row["name"]
            trainee.password = row["password"]
            trainee.phonenumber = row["phone_number"]
            trainee.gender = row["gender"]
            trainee.birthday = row["birthday"]
            res.append(trainee)
            row = cur.fetchone()
        cur.close()
        return res
    def enter_group(self, group):
        from flask import g
        connection = g.connection
        cur = connection.cursor()
        try:
            cur.callproc("ENTER_GROUP", (group.uid, self.uid,0))
            cur.execute('SELECT @_ENTER_GROUP_2')
            res = cur.fetchone()["@_ENTER_GROUP_2"]
            if res != 0:
                print(res)
                return False
        except err:
            print(err)
            return False
        connection.commit()
        return True
    def insert(self):
        from flask import g
        connection = g.connection
        condition = False
        condition = condition or (self.gender is None)
        condition = condition or (self.birthday is None)
        condition = condition or (self.name is None)
        condition = condition or (self.password is None)
        condition = condition or (self.phonenumber is None)
        if condition:
            return False
        try:
            cur = connection.cursor()
            arg =  (self.phonenumber, self.name, self.password)
            cur.execute("INSERT INTO tb_users (phone_number, name, password) VALUES (%s, %s, password(%s))",arg)
            cur.execute("SELECT last_insert_id() as 'uid'")
            row = cur.fetchone()
            self.uid = row["uid"]
            arg = (self.uid, self.gender, self.birthday)
            cur.execute("INSERT INTO tb_trainees (user_uid, gender, birthday) VALUES (%s, %s, %s)", arg)
            connection.commit()
            cur.close()
        except:
            return False
        return True
    def get_groups(self):
        from flask import g
        connection = g.connection
        cur = connection.cursor()
        condition = False
        condition = condition or (self.uid is None)
        if condition:
            return NotFoundAccount()
        arg =  (self.uid)
        gyms = dict()
        openers = dict()
        cur.execute("SELECT * FROM  v_user_groups WHERE user_uid = %s", arg)
        res = list();
        row = cur.fetchone()
        while row is not None:
            group = dict()
            gym_uid = row["gym_uid"]
            opener_uid = row["opener_uid"]
            if  not gym_uid in  gyms:
                gyms[gym_uid] = Gym.find(gym_uid)
            if not opener_uid in openers:
                openers[opener_uid] = User.find(opener_uid)
            group["gym"] = gyms[gym_uid]
            group["opener"] = openers[opener_uid]
            group["uid"] = row["uid"]
            group["opened"] = row["opened"]
            
            group["capacity"] = row["capacity"]
            group["comment"] = row["comment"]
            group["time"] = row["time"]
            group["charge"] = row["charge"]
            group["daysOfWeek"] = DaysOfWeeks(row["uid"])
            group["start_date"] = row["start_date"]
            group["period"] = row["period"]
            group["title"] = row["title"]
            g = Group(**group)
            res.append(g)
            row = cur.fetchone()
        cur.close()
        return res
class Gym:
    uid = None#int
    latitude = None
    longitude = None
    name = None
    address = None
    def __init__(self, uid:int, lat:float, long:float, name:str, address:str):
        self.uid = uid
        self.latitude = lat
        self.longitude = long
        self.name = name
        self.address = address
    def insert(self):
        from flask import g
        connection = g.connection
        cur = connection.cursor()
        arg =  (self.name, self.address, self.latitude, self.longitude)
        try:
            cur.execute("INSERT INTO tb_gyms (name,address, latitude, longitude) VALUES (%s, %s, %s, %s)", arg)
        except Error as e:
            print(e.error_msg)
            return False
        connection.commit()
        return True
    def delete(self):
        from flask import g
        connection = g.connection
        cur = connection.cursor()
        arg =  (self.uid)
        try:
            cur.execute("DELETE FROM  tb_gyms WHERE uid = %s", arg)
        except Error as e:
            print(e.error_msg)
            return False
        connection.commit()
    @staticmethod
    def find(uid):
        from flask import g
        connection = g.connection
        cur = connection.cursor()
        arg =  (uid)
        cur.execute("SELECT * FROM  tb_gyms WHERE uid = %s", arg)
        row = cur.fetchone()
        if row is None:
            return None
        lat = row["latitude"]
        lon = row["longitude"]
        name = row["name"]
        address = row["address"]
        gym = Gym(uid, lat, lon, name, address)
        return gym
    def get_groups(self):
        from flask import g
        connection = g.connection
        cur = connection.cursor()
        condition = False
        condition = condition or (self.uid is None)
        if condition:
            return NotFoundAccount()
        arg =  (self.uid)
        gyms = dict()
        openers = dict()
        cur.execute("SELECT * FROM  tb_groups WHERE gym_uid = %s", arg)
        res = list();
        row = cur.fetchone()
        while row is not None:
            group = dict()
            gym_uid = row["gym_uid"]
            opener_uid = row["opener_uid"]
            if not opener_uid in openers:
                openers[opener_uid] = User.find(opener_uid)
            group["gym"] = self
            group["opener"] = openers[opener_uid]
            group["uid"] = row["uid"]
            group["opened"] = row["opened"]
            group["capacity"] = row["capacity"]
            group["comment"] = row["comment"]
            group["time"] = row["time"]
            group["charge"] = row["charge"]
            group["daysOfWeek"] = DaysOfWeeks(row["uid"])
            group["start_date"] = row["start_date"]
            group["period"] = row["period"]
            group["title"] = row["title"]
            g = Group(**group)
            res.append(g)
            row = cur.fetchone()
        cur.close()
        return res
    @staticmethod
    def list():
        connection = g.connection
        cur = connection.cursor()
        cur.execute("SELECT * FROM tb_gyms")
        res = list();
        row = cur.fetchone()
        while row is not None:
            gym = Gym(row["uid"], row["latitude"],row["longitude"],row["name"],row["address"] )
            res.append(gym)
            row = cur.fetchone()
        cur.close()
        return res
class DaysOfWeeks:
    group_uid = -1
    def __init__(self, uid:int):
        self.group_uid = uid
    def get(self):
        from flask import g
        connection = g.connection
        cur = connection.cursor()
        cur.execute("SELECT dayOfWeek FROM  tb_daysOfWeeks WHERE uid = %s", (self.group_uid))
        rows = cur.fetchall()
        return set(row['dayOfWeek'] for row in rows)
class Group:
     uid = None #int
     gym = None #Gym
     opened = None  #boolean
     opener = None #opener
     capacity = None #int
     comment = None #String
     time = None #
     charge = None
     daysOfWeek = None
     start_date = None
     period = None
     title = None#string
     user_count = None#int
     def __init__(self, uid, gym, opened, opener, capacity, comment, time,charge, daysOfWeek, start_date, period, title):

        self.uid = uid
        if self.uid is not None:
            self.uid = int(self.uid)
            from flask import g
            connection = g.connection
            cur = connection.cursor()
            cur.execute("SELECT * from v_count_in_group where group_uid = %s", (self.uid))
            row = cur.fetchone()
            if row is not None:
                self.user_count = row["count"]
        self.gym = gym
        self.capacity = capacity
        self.opened = "Y" == opened 
        self.opener = opener
        self.time = time
        self.comment = comment
        self.charge = charge
        self.title = title
        self.period = period
        self.start_date = start_date
        
        
        if type(daysOfWeek) is DaysOfWeeks:
            self.daysOfWeek = daysOfWeek.get()
        else:
            self.daysOfWeek =set(x.strip() for x in daysOfWeek.split(","))
        self.start_date = start_date
        self.period = period
     def insert(self):
        from flask import g
        connection = g.connection
        cur = connection.cursor()
        daysOfWeek =("{}," * len(self.daysOfWeek)).format(*self.daysOfWeek)[:-1]
        arg =  (self.gym.uid, self.opener.uid, self.opened, self.capacity, self.time.strftime("%H:%M:00"), self.charge, self.comment, self.title, self.period, self.start_date)
        columns = "gym_uid,opener_uid, opened, capacity, time, charge, comment, title, period, start_date"
        args_str = ("%s," * len(arg))[:-1]
        table = "tb_groups"
        qry = "INSERT INTO %s (%s) VALUES (%s)"%(table, columns, args_str)
        print(qry)
        cur.execute(qry, arg)
        table = "tb_daysOfWeeks"
        columns = "uid, dayOfWeek"
        args_str = "%s, %s"
        qry = "INSERT INTO %s (%s) VALUES (%s)"%(table, columns, args_str)
        args_list = list((cur.lastrowid, x) for x in self.daysOfWeek)
        cur.executemany(qry, args_list)
        connection.commit()
        return True
     @staticmethod
     def find(uid):
        from flask import g
        connection = g.connection
        cur = connection.cursor()
        arg =  (uid)
        cur.execute("SELECT * FROM  tb_groups WHERE uid = %s", arg)
        row = cur.fetchone()
        if row is None:
            return None
        group = dict()
        gym_uid = row["gym_uid"]
        opener_uid = row["opener_uid"]
        group["gym"] = Gym.find(gym_uid)
        group["opener"] = User.find(opener_uid)
        group["uid"] = row["uid"]
        group["opened"] = row["opened"]
        group["capacity"] = row["capacity"]
        group["comment"] = row["comment"]
        group["time"] = row["time"]
        group["charge"] = row["charge"]
        group["daysOfWeek"] = DaysOfWeeks(row["uid"])
        group["start_date"] = row["start_date"]
        group["period"] = row["period"]
        group["title"] = row["title"]
        return Group(**group)
     @staticmethod
     def get_list(rat, long, rad):
        from flask import g
        connection = g.connection
        cur = connection.cursor()
        if None in (rat, long, rad):
            cur.execute("""SELECT * FROM  tb_groups""")
        else:
            cur.execute("""SELECT * FROM  tb_groups
           where gym_uid in 
           (SELECT uid 
           WHERE POW(%s,2) > POW(tb_gyms.latitude - %s, 2) + POW(tb_gyms.longitude - %s, 2) 
            """, (float( rat), float( long),float( rad)))
        row = cur.fetchone()
        res = list()
        while row is not None:
            group = dict()
            gym_uid = row["gym_uid"]
            opener_uid = row["opener_uid"]
            group["gym"] = Gym.find(gym_uid)
            group["opener"] = User.find(opener_uid)
            group["uid"] = row["uid"]
            group["opened"] = row["opened"]
            group["capacity"] = row["capacity"]
            group["comment"] = row["comment"]
            group["time"] = row["time"]
            group["charge"] = row["charge"]
            group["daysOfWeek"] = DaysOfWeeks(row["uid"])
            group["start_date"] = row["start_date"]
            group["period"] = row["period"]
            group["title"] = row["title"]
            row = cur.fetchone()
            res.append(Group(**group))
        return res
class Image:
    def __init__(self, image_name:str, uploader, data, image_type):
        if type(uploader) is int:
            self.uploader_uid = uploader
        else:
            self.uploader_uid = uploader.uid
        self.image_name = image_name
        self.data = data
        self.image_type = image_type
    def upload(self):
        from flask import g
        connection = g.connection
        cur = connection.cursor()
        arg =  (self.uploader_uid, self.image_name, self.image_type)
        columns = "uploader_uid, image_name, image_type"
        args_str = ("%s," * len(arg))[:-1]
        table = "tb_images"
        qry = "INSERT INTO %s (%s) VALUES (%s)"%(table, columns, args_str)
        cur.execute(qry, arg)
        fp = open(app.config['UPLOAD_FOLDER'] +"/images/" + self.image_name, "wb+")
        fp.write(self.data)
        fp.close()
        connection.commit()
    @staticmethod
    def get_list(uploader, offset = 0, count = 9):

        return None
class MeasurementInfo:
    def __init__(self, image_name:str, uploader, data, image_type, weight, muscle, fat):
        if type(uploader) is int:
            self.uploader_uid = uploader
        else:
            self.uploader_uid = uploader.uid
        self.image_name = image_name
        self.data = data
        self.image_type = image_type
        self.weight = weight
        self.muscle = muscle
        self.fat = fat
        pass
    def upload(self):
        from flask import g
        connection = g.connection
        cur = connection.cursor()
        arg =  (self.uploader_uid, self.image_name, self.image_type,self.weight, self.muscle, self.fat)
        columns = "uploader_uid, image_name, image_type, weight, muscle, fat"
        args_str = ("%s," * len(arg))[:-1]
        table = "tb_measurement_infos"
        qry = "INSERT INTO %s (%s) VALUES (%s)"%(table, columns, args_str)
        cur.execute(qry, arg)
        fp = open(app.config['UPLOAD_FOLDER'] +"/images/" + self.image_name, "wb+")
        fp.write(self.data)
        fp.close()
        connection.commit()
from flask import g
from pymysql import Error
import datetime
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
    def __init__(self):
        self.uid = None
        self.name = None
        self.password = None
        self.phonenumber = None
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
        if row["gym_uid"] is None:
            user = Trainee()
            user.gender = row["gender"]
            user.birthday = row["birthday"]
        else:
            user = Trainer()
            user.gym_uid = row["gym_uid"]
        user.name = row["name"]
        user.uid = row["uid"]
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
            res = Trainee()
            res.uid = int(id)
            res.name = name
            res.phonenumber = self.phonenumber
            res.password = None
            res.gender = row["gender"]
            res.gender = row["birthday"]
            cur.close()
            return res
        cur.execute("SELECT * FROM tb_trainers WHERE user_uid = %s",  args)
        row = cur.fetchone()

        if row is not None:
            res = Trainer()
            res.uid = int(id)
            res.name = name
            res.phonenumber = self.phonenumber
            res.password = None
            res.gym_uid = row["gym_uid"]
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
        if row["gym_uid"] is None:
            user = Trainee()
            user.gender = row["gender"]
            user.birthday = row["birthday"]
        else:
            user = Trainer()
            user.gym_uid = row["gym_uid"]
        user.name = row["name"]
        user.uid = row["uid"]
        return user
class Trainer(User):
    gym_uid = None#int()
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
            group["comments"] = row["comments"]
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
        arg =  (self.uid, group.uid)
        columns = "trainee_uid,group_uid"
        args_str = ("%s," * len(arg))[:-1]
        table = "tb_users_in_group"
        qry = "INSERT INTO %s (%s) VALUES (%s)"%(table, columns, args_str)
        connection = g.connection
        cur = connection.cursor()
        try:
            cur.execute(qry, arg)
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
            group["comments"] = row["comments"]
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
            group["comments"] = row["comments"]
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
     comments = None #String
     time = None #
     charge = None
     daysOfWeek = None
     start_date = None
     period = None
     title = None#string
     def __init__(self, uid, gym, opened, opener, capacity, comments, time,charge, daysOfWeek, start_date, period, title):
        self.uid = uid
        self.gym = gym
        self.capacity = capacity
        self.opened = "Y" == opened 
        self.opener = opener
        self.time = time
        self.comments = comments
        self.charge = charge
        self.title = title
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
        arg =  (self.gym.uid, self.opener.uid, self.opened, self.capacity, self.time.strftime("%H:%M:00"), self.charge, self.comments, self.title)
        columns = "gym_uid,opener_uid, opened, capacity, time, charge, comments, title"
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
        group["comments"] = row["comments"]
        group["time"] = row["time"]
        group["charge"] = row["charge"]
        group["daysOfWeek"] = DaysOfWeeks(row["uid"])
        group["start_date"] = row["start_date"]
        group["period"] = row["period"]
        group["title"] = row["title"]
        return Group(**group)
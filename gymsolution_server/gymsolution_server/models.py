from gymsolution_server import connection
import datetime
class User:
    uid = None
    name = None#str()
    password = None#str()
    phonenumber = None#str()
    def __init__(self):
        self.uid = None
        self.name = None
        self.password = None
        self.phonenumber = None
    def check_permission(self):
        cur = connection.cursor()
        args = (self.phonenumber, self.password)
        cur.execute("SELECT * FROM tb_users WHERE phone_number = %s AND password = password(%s)",  args)
        row = cur.fetchone()
        if row is None:
            return None
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
            return res
        return None
class Trainer(User):
    gym_uid = None#int()
    def insert(self):
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
class Trainee(User):
    gender = None#str()
    birthday = None#datetime.date.
    def insert(self):
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
    @staticmethod
    def list():
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
import os
import pickle


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.group_id = 0
        self.history = []


class UserDB:
    def __init__(self):
        self.user_dict = {}  # 保存用户名 -> 用户OBJ

    def user_check_in(self, username, password):
        user = self.user_dict.get(username)
        if user is not None:
            if user.password == password:
                return 0
        return -1

    def add_user(self, username, password, group_id):
        user = self.user_dict.get(username)
        if user is None:
            user = User(username, password)
            user.belong_group_id = group_id
            self.user_dict[username] = user
            return 0
        return -1

    def check_property(self, username, group_id):
        if self.get_user_property(username) >= group_id:
            return 0  # ok
        else:
            return -1  # 权限不足

    def get_user_property(self, username):
        user = self.user_dict.get(username)
        if user is None:
            return -2  # 用户不存在
        return user.group_id  # ok

    def update_property(self, username, group_id):
        user = self.user_dict.get(username)
        if user is None:
            return -2
        user.group_id = group_id
        return 0

    def update_history(self, username, action, time):
        user = self.user_dict.get(username)
        if user is None:
            return -2
        user.history.append((action, time))
        return 0

    def get_history(self, username):
        user = self.user_dict.get(username)
        if user is None:
            return -2
        return user.history


class UserManager:
    def __init__(self):
        self.user_db = UserDB()

    def load_archive_exist(self):
        for root, dirs, files in os.walk("."):
            for file_ in files:
                if file_.startswith('user_db'):
                    file_ = open(file_, "r+b")
                    self.user_db = pickle.load(file_)
                    file_.close()
                    return

    def save_archive(self):
        file_ = open("user_db", "w+b")
        pickle.dump(self.user_db, file_)
        file_.close()

    def login(self, username, password):
        return self.user_db.user_check_in(username, password)

    def register(self, username, password):
        return self.user_db.add_user(username, password, 0)

    def assign_user_group(self, username, group_id):
        return self.user_db.update_property(username, group_id)

    def check_property(self, username, target_group_id):
        return self.user_db.check_property(username, target_group_id)

    def look_up_property(self, username):
        return self.user_db.get_user_property(username)

    def update_history(self, username, action, time):
        return self.user_db.update_history(username, action, time)

    def get_user_history(self, username):
        return self.user_db.get_history(username)

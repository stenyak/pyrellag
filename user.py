import json

max_id = 0

class UserList():
    def __init__(self):
        self.users = []
        try:
            with open("profiles.json", "r") as f:
                data = json.loads(f.read())
            for i in data:
                self.add_new(i["name"], i["email"], i["openid"], i["groups"], i["id"])
                self.check_max_id(i["id"])
        except IOError:
            pass # no profiles stored yet. no worries
    def check_max_id(self, id):
        global max_id
        max_id = max(id, max_id)
    def get_by_openid(self, openid):
        for u in self.users:
            if u["openid"] == openid:
                return u
        return None
    def get_by_id(self, id):
        assert(isinstance(id, int))
        for u in self.users:
            if u["id"] == id:
                return u
        return None
    def get_all(self):
        return self.users
    def save(self):
        self.users = sorted(self.users, key=lambda u: u["id"]) # always keep it tidy and sorted :-D
        with open("profiles.json", "w") as f:
            f.write(json.dumps(self.users, indent=4, sort_keys=True, separators=(",", " : ")))
            f.flush()
    def set(self, user):
        self.users = [u for u in self.users if u["id"] != user["id"]]
        assert(isinstance(user["id"], int))
        self.add(user)
        self.check_max_id(id)
        self.save()
    def add(self, user):
        self.users.append(user)
        self.save()
    def add_new(self, name, email, openid, groups, id=None):
        user = {}
        if id is None:
            global max_id
            id = max_id
            max_id += 1
        assert(isinstance(id, int))
        self.check_max_id(id)
        user["id"] = id
        user["name"] = name
        user["email"] = email
        user["openid"] = openid
        user["groups"] = groups
        self.add(user)
    def delete(self, user):
        self.users = [u for u in self.users if u["id"] != user["id"]]
        self.save()
    def total(self):
        return len(self.users)

from werkzeug.security import check_password_hash, generate_password_hash


class User:
    def __init__(self, id, username, password, fullname="") -> None:
        self.id = id
        self.username = username
        self.password = password
        self.fullname = fullname

    @classmethod
    def check_password(self, hashed_password, password):
        return check_password_hash(hashed_password, password)


print(generate_password_hash("usern"))
# pbkdf2:sha256:150000$NKpJOe2v$256244a78faa08573f0833292fbd9fce7e37b73faf57882e13c0d2a338201a35

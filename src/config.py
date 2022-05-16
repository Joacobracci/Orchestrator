class Config:
    SECRET_KEY = ""


class DevelopmentConfig(Config):
    DEBUG = True
    MYSQL_HOST = "localhost"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "123456"
    MYSQL_DB = "flask_login"


config = {"development": DevelopmentConfig}

# config.py
class Config:
    SECRET_KEY = "my_super_key"  # Задайте унікальне значення, наприклад: "my_super_secret_key"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:1111@localhost/maintenance_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True

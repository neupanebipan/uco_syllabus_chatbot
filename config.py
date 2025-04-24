import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "your_secret_key_here")
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'database.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "your_secret_key_here")
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/database.sqlite'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
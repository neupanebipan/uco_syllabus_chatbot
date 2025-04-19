
from app import db

class Syllabus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    course_number = db.Column(db.String(20), nullable=False)
    course_name = db.Column(db.String(100), nullable=False)







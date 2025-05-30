from extensions import db

class Professor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    syllabi = db.relationship('Syllabus', backref='professor', lazy=True)

class Syllabus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    course_number = db.Column(db.String(20), nullable=False)
    course_name = db.Column(db.String(100), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'), nullable=False)


from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import os
from forms import LoginForm, UploadForm
from utils.llama_api import call_llm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/database.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if not os.path.exists('uploads'):
    os.makedirs('uploads')
if not os.path.exists('instance'):
    os.makedirs('instance')


ALLOWED_EXTENSIONS = {'pdf'}
db = SQLAlchemy(app)
from models import Syllabus

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == 'professor' and form.password.data == 'password':
            session['user'] = form.username.data
            return redirect(url_for('upload'))
        flash('Invalid credentials')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        return redirect(url_for('login'))
    form = UploadForm()
    if form.validate_on_submit():
        file = form.pdf.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            new_syllabus = Syllabus(
                filename=filename,
                department=form.department.data,
                course_number=form.course_number.data,
                course_name=form.course_name.data
            )
            db.session.add(new_syllabus)
            db.session.commit()
            flash('Syllabus uploaded successfully')
            return redirect(url_for('upload'))
    return render_template('upload.html', form=form)

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        department = request.form['department']
        course_number = request.form['course_number']
        question = request.form['question']
        syllabus = Syllabus.query.filter_by(department=department, course_number=course_number).first()
        if not syllabus:
            return render_template('chat.html', error='Course not found')
        response = call_llm(question, syllabus.filename)
        return render_template('chat.html', response=response)
    return render_template('chat.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import os
from config import Config
from extensions import db
from forms import LoginForm, UploadForm
from models import Syllabus, Professor
from utils.llama_api import call_llm_multi

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
if not os.path.exists('instance'):
    os.makedirs('instance')


def seed_professors():
    with app.app_context():
        if Professor.query.count() == 0:
            professors = [
                Professor(username='fujincheng', password='fu1234'),
                Professor(username='zhang', password='zhang123'),
                Professor(username='tmorris', password='tm123')
            ]
            db.session.bulk_save_objects(professors)
            db.session.commit()

with app.app_context():
    db.create_all()
    seed_professors()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    next_page = request.args.get('next')
    if form.validate_on_submit():
        prof = Professor.query.filter_by(username=form.username.data).first()
        if prof and form.password.data == prof.password:
            session['user'] = prof.username
            return redirect(next_page or url_for('upload'))
        flash('Invalid credentials')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        return redirect(url_for('login', next=request.url))
    form = UploadForm()
    if form.validate_on_submit():
        file = form.pdf.data
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            new_syllabus = Syllabus(
                filename=filename,
                department=form.department.data.strip().lower(),
                course_number=form.course_number.data.strip().lower(),
                course_name=form.course_name.data.strip()
            )
            db.session.add(new_syllabus)
            db.session.commit()
            flash('Syllabus uploaded successfully')
            return redirect(url_for('upload'))
    return render_template('upload.html', form=form)

@app.route('/chat', methods=['POST'])
def chat():
    question = request.form['question'].strip()
    department = request.form.get('department', '').strip().lower()
    course_number = request.form.get('course_number', '').strip().lower()

    if department and course_number:
        syllabi = Syllabus.query.filter_by(department=department, course_number=course_number).all()
    else:
        syllabi = Syllabus.query.all()

    responses = []
    for s in syllabi:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], s.filename)
        response_text = call_llm_multi(question, filepath)
        responses.append({
            'department': s.department,
            'course_number': s.course_number,
            'course_name': s.course_name,
            'answer': response_text
        })

    return render_template('chat_results.html', question=question, responses=responses)

if __name__ == '__main__':
    app.run(debug=True)
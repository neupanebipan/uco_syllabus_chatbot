# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
import os
from config import Config
from extensions import db
from forms import LoginForm, UploadForm, SignupForm
from models import Syllabus, Professor
from utils.llama_api import call_llm_multi

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
if not os.path.exists('instance'):
    os.makedirs('instance')

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return redirect(url_for('chat'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        existing_prof = Professor.query.filter_by(username=form.username.data).first()
        if existing_prof:
            flash('Username already exists. Please choose another.', 'error')
            return redirect(url_for('signup'))
        new_prof = Professor(username=form.username.data, password=form.password.data)
        db.session.add(new_prof)
        db.session.commit()
        flash('Account created successfully. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    next_page = request.args.get('next')
    if form.validate_on_submit():
        prof = Professor.query.filter_by(username=form.username.data).first()
        if prof and form.password.data == prof.password:
            session['user'] = prof.username
            session['user_id'] = prof.id
            return redirect(next_page or url_for('upload'))
        flash('Invalid credentials')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session or 'user_id' not in session:
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
                course_name=form.course_name.data.strip(),
                professor_id=session['user_id']
            )
            db.session.add(new_syllabus)
            db.session.commit()
            flash('Syllabus uploaded successfully')
            return redirect(url_for('upload'))
    syllabi = Syllabus.query.filter_by(professor_id=session['user_id']).all()
    return render_template('upload.html', form=form, syllabi=syllabi)

@app.route('/delete/<int:syllabus_id>', methods=['POST'])
def delete_syllabus(syllabus_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    syllabus = Syllabus.query.get_or_404(syllabus_id)
    if syllabus.professor_id != session['user_id']:
        flash('Unauthorized access')
        return redirect(url_for('upload'))
    db.session.delete(syllabus)
    db.session.commit()
    flash('Syllabus deleted successfully')
    return redirect(url_for('upload'))

@app.route('/chat', methods=['GET'])
def chat():
    chat_history = session.get('chat_history', [])
    return render_template('chat.html', chat_history=chat_history)

@app.route('/send_message', methods=['POST'])
def send_message():
    question = request.form['question'].strip()
    department = request.form.get('department', '').strip().lower()
    course_number = request.form.get('course_number', '').strip().lower()

    if department and course_number:
        syllabi = Syllabus.query.filter_by(department=department, course_number=course_number).all()
    elif department:
        syllabi = Syllabus.query.filter_by(department=department).all()
    elif course_number:
        syllabi = Syllabus.query.filter_by(course_number=course_number).all()
    else:
        syllabi = Syllabus.query.all()

    clean_responses = []

    if syllabi:
        for s in syllabi:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], s.filename)
            response = call_llm_multi(question, filepath)

            if isinstance(response, dict) and 'content' in response:
                answer_text = response['content']
            elif isinstance(response, dict) and 'response' in response and 'content' in response['response']:
                answer_text = response['response']['content']
            else:
                answer_text = "Sorry, there was an error retrieving information from this syllabus."

            course_info = f"📘 {s.course_number.upper()} - {s.course_name} ({s.department})"
            full_response = f"{course_info}\n{answer_text.strip()}"
            clean_responses.append(full_response)
    else:
        clean_responses.append("Sorry, I couldn't find any relevant course materials.")

    combined_response = "\n\n".join(clean_responses)

    history = session.get('chat_history', [])
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": combined_response})
    session['chat_history'] = history

    return jsonify({"response": combined_response})

@app.route('/reset_chat')
def reset_chat():
    session.pop('chat_history', None)
    return redirect(url_for('chat'))

if __name__ == '__main__':
    app.run(debug=True)

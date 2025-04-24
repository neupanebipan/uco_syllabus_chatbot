# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class UploadForm(FlaskForm):
    department = SelectField('Department', choices=[
        ('mathematics', 'Mathematics and Statistics'),
        ('computer_science', 'Computer Science'),
        ('business', 'Business'),
        ('psychology', 'Psychology')
    ], validators=[DataRequired()])
    course_number = StringField('Course Number', validators=[DataRequired()])
    course_name = StringField('Course Name', validators=[DataRequired()])
    pdf = FileField('PDF File', validators=[FileAllowed(['pdf'], 'PDF only!')])
    submit = SubmitField('Upload')

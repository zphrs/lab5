from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class SignupForm(FlaskForm):
    username = StringField('Username', validators=[Length(min=1, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Signup')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[Length(min=1, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class NewpostForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

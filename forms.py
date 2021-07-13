from flask.app import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField
from wtforms.validators import InputRequired, Email
import email_validator
from wtforms.widgets.core import Input

class SignupForm(FlaskForm):
    name=StringField('Name', validators=[InputRequired()])
    username=StringField('Username', validators=[InputRequired()])
    password=PasswordField('Password', validators=[InputRequired()])
    confirm_password=PasswordField('Confirm Password', validators=[InputRequired()])
    email=StringField('Email', validators=[InputRequired(), Email()])
    
class EditUserForm(FlaskForm):
    name=StringField('Name', validators=[InputRequired()])
    username=StringField('Username', validators=[InputRequired()])
    email=StringField('Email', validators=[InputRequired()])
    password=PasswordField('Password', validators=[InputRequired()])

class LoginForm(FlaskForm):
    username=StringField('Username', validators=[InputRequired()])
    password=PasswordField('Password', validators=[InputRequired()])

class SearchForm(FlaskForm):
    search_term=StringField('Movie/TV Show', validators=[InputRequired()])
    type=SelectField('Movie or TV Show?', choices=[('movie', 'Movie'), ('tv', 'TV Show')])

class CommentForm(FlaskForm):
    title=StringField('Comment Title', validators=[InputRequired()])
    content=TextAreaField('Comment', validators=[InputRequired()])
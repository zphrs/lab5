import sys
from dotenv import load_dotenv
from flask import Flask, flash, render_template, request, url_for, redirect, jsonify, session
from models.models import Db, User, Post
from forms.forms import SignupForm, LoginForm, NewpostForm
from os import environ
from passlib.hash import sha256_crypt
import datetime
import psycopg2
import gunicorn
from flask_heroku import Heroku
import csv 
postgresPassword = ''
# opening the CSV file 
with open('passwords.csv', mode ='r') as file:
    # reading the CSV file 
    dictReader = csv.DictReader(file)
    for row in dictReader:
        dictReader = row
    postgresPassword = dictReader['postgres']

load_dotenv('.env')

app = Flask(__name__)
heroku = Heroku(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:'+postgresPassword+'@localhost:5432/lab5'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = environ.get('SECRET_KEY')
Db.init_app(app)


#GET /
@app.route('/')
@app.route('/index')
def index():
    #Control by login status
    if 'username' in session:
        session_user = User.query.filter_by(username=session['username']).first()
        posts = Post.query.filter_by(author=session_user.uid).all()
        for post in posts:
            post.username=User.query.filter_by(uid=post.author).first().username
        return render_template('index.html', title='Home', posts=posts, session_username=session_user.username)
    else:
        all_posts = Post.query.all()
        all_users = []
        for post in all_posts:
            post.username=User.query.filter_by(uid=post.author).first().username
        
        return render_template('index.html', title='Home', posts=all_posts, users=all_users)

@app.route('/about')
def about():
    return render_template('about.html', title='About')
#GET & POST /login
@app.route('/login', methods=['GET', 'POST'])
def login():
    #Init form
    form = LoginForm()

    #If post
    if request.method == 'POST':

        #Init credentials from form request
        username = request.form['username']
        password = request.form['password']
        #Init user by Db query
        user = User.query.filter_by(username=username).first()

        #Control login validity
        if user is None or not sha256_crypt.verify(password, user.password):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        else:
            session['username'] = username
            return redirect(url_for('index'))

    #If GET
    else:
        return render_template('login.html', title='Login', form=form)


#POST /logout
@app.route('/logout', methods=['POST'])
def logout():
    #Logout
    session.clear()
    return redirect(url_for('index'))


#GET & POST /newpost
@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    #Init form
    form = NewpostForm()

    #If POST
    if request.method == 'POST':

        #Init user from poster
        session_user = User.query.filter_by(username=session['username']).first()

        #Init content from form request
        content = request.form['content']
        date = datetime.datetime.now()
        #Create in DB
        new_post = Post(author=session_user.uid, content=content, creation_date=date)
        Db.session.add(new_post)
        Db.session.commit()

        return redirect(url_for('index'))

    #If GET
    else:
        if 'username' in session:
            return render_template('newpost.html', title='Newpost', form=form)
        else:
            flash('Login before making a post.')
            return redirect(url_for('login'))
        


#GET & POST /signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    #Init form
    form = SignupForm()

    #IF POST
    if request.method == 'POST':

        #Init credentials from form request
        username = request.form['username']
        password = request.form['password']
        date = datetime.datetime.now()
        #Init user from Db query
        existing_user = User.query.filter_by(username=username).first()

        #Control new credentials
        if existing_user:
            flash('The username already exists. Please pick another one.')
            return redirect(url_for('signup'))
        else:
            user = User(username=username, password=sha256_crypt.hash(password), creation_date=date)
            Db.session.add(user)
            Db.session.commit()
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('login'))

    #IF POST
    else:
        return render_template('signup.html', title='Signup', form=form)
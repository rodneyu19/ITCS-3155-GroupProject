from flask import Flask, render_template, request, redirect, flash, url_for
from src.models import db, Post
from dotenv import load_dotenv
import os
import urllib.parse
from forms import RegistrationForm, LoginForm

app = Flask(__name__)

load_dotenv()

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

if None in (os.getenv("DB_USER"), os.getenv("DB_PASS"), os.getenv("DB_HOST"), os.getenv("DB_PORT"), os.getenv("DB_NAME")):
    raise ValueError("Fix the variables in your .env lmao")

app.config['SQLALCHEMY_DATABASE_URI'] = \
    f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASS")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}'

db.init_app(app)

@app.get('/')
@app.route('/home', methods=['GET']) 
def index():
    all_posts = Post.query.all()
    return render_template('home.html', all_posts=all_posts)

@app.get('/post/new')
def create_post_form():
    return render_template('create_post.html')

@app.post('/post/new')
def create_post():
    title = request.form.get('title')
    body = request.form.get('body')
    link = request.form.get('link')
    new_post = Post(title=title, body=body, link=link)
    db.session.add(new_post)
    db.session.commit()
    return redirect('/')

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(('/home'))
    return render_template('register.html', title='register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect('/home')
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='login', form=form)
    
@app.get('/spotifylogin')
def loginReq():
    request = {
        'client_id': '2bc0ff7c68354c1b9f2625ba6f642a63',
        'response_type': 'code',
        'scope': 'user-read-private',
        'redirect_uri': 'https://127.0.0.1:5000/home',
        'show_dialog': False
    } 
    
    auth_url = f"'https://accounts.spotify.com/authorize'?{urllib.parse.urlencode(request)}"
    
    return redirect(auth_url)
    

@app.get('/profile')
def profile():
    return render_template('profile.html')

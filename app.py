
from flask import Flask, render_template, request, redirect, flash, url_for, session

from src.models import db, Post
from dotenv import load_dotenv
from forms import SearchForm
import os
import urllib.parse
from forms import RegistrationForm, LoginForm
from spotipy.oauth2 import SpotifyOAuth
from time import time

app = Flask(__name__)

load_dotenv()

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
TOKEN_INFO = 'token_info'

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
        return redirect(('home'))
    return render_template('register.html', title='register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect('home')
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='login', form=form)

@app.route("/spotifylogin")
def loginwithSpotify():
    authUrl = create_spotify_oauth().get_authorize_url()
    return redirect(authUrl)

@app.route('/spotifyredirect')
def spotifyRedirect():
    session.clear()
    code = request.args.get('code')
    session[TOKEN_INFO] =  create_spotify_oauth().get_access_token(code)
    return redirect(url_for('profile',_external=True))

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        redirect(url_for('login', _external=False))
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if(is_expired):
        spotify_oauth = create_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])

    return token_info

@app.get('/profile')
def profile():
    return render_template('profile.html')

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id =  '2bc0ff7c68354c1b9f2625ba6f642a63',
        client_secret = '75f01422207741a6a817a4b9fd1b4f52',
        redirect_uri =  url_for("spotifyRedirect", _external = True),
        scope= 'user-read-private'
    )
    
# Pass though Navbar
@app.context_processor
def base():
	form = SearchForm()
	return dict(form=form)

# Search Funciton
@app.route('/search', methods=['POST'])
def search():
	forms = SearchForm()
	posts = Posts.query
	if form.validate_on_submit():
		# Get data from submitted form
		post.searched = form.searched.data
		# Query the Database
		posts = posts.filter(Posts.body.like('%' + post.searched + '%'))
		posts = post.order_by(Posts.title).all()
		
		return render_template("search.html", 
								form = form, 
								searched = post.searched,
								posts = posts)
	
if __name__ == '__main__':
	app.run(debug=True)


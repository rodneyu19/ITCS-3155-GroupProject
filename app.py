from flask import Flask, render_template, request, redirect, flash, url_for, session
from src.models import db, Post, User
from dotenv import load_dotenv
import os
from forms import RegistrationForm, LoginForm, SearchForm
from spotipy.oauth2 import SpotifyOAuth
from flask_bcrypt import Bcrypt
import time


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
        hashedPass = Bcrypt.generate_password_hash(form.password.data)
        user = User(username = form.username.data, password = hashedPass)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    session.clear()
    session[TOKEN_INFO] = None
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

# Pass though Navbar
@app.context_processor
def base():
	form = SearchForm()
	return dict(form=form)

# Search Funciton
@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    posts = Post.query
    if form.validate_on_submit():
        if form.searched.data != None:
            # Get data from submitted form
            Post.searched = form.searched.data
            # Query the Database
            posts = posts.filter(Post.body.like('%' + Post.searched + '%'))
            posts = Post.order_by(Post.title).all()
            return render_template("search.html", form = form, searched = Post.searched, posts = posts)
        else:
            error = "Cant search nothing"
            return redirect(('home'))
    

@app.get('/profile')
def profile():
    token = session.get(TOKEN_INFO, None)
    if token != None:
        flash('You have been logged in!', 'success')
    return render_template('profile.html')

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

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id =  '2bc0ff7c68354c1b9f2625ba6f642a63',
        client_secret = '75f01422207741a6a817a4b9fd1b4f52',
        redirect_uri =  url_for("spotifyRedirect", _external = True),
        scope= 'user-read-private'
    )

@app.get('/post/delete/<int:post_id>')
def delete_post(post_id):
    print(post_id)
    post = Post.query.get(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/')

@app.route('/post/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Post.query.get(post_id)
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.body = request.form.get('body')
        post.link = request.form.get('link')
        db.session.commit()
        flash('Post updated successfully', 'success')
        return redirect('/')

    return render_template('edit_post.html', post=post, post_id=post_id)

	
if __name__ == '__main__':
	app.run(debug=True)
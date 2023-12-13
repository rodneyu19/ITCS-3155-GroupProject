from flask import Flask, render_template, request, redirect, flash, url_for, session
from src.models import db, Post, Users, Comment
from dotenv import load_dotenv
import os
from forms import RegistrationForm, LoginForm, SearchForm, EditProfileForm
from spotipy.oauth2 import SpotifyOAuth
import spotipy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from sqlalchemy import desc
import time


app = Flask(__name__)
loginManager = LoginManager(app)
bcrypt = Bcrypt(app)
load_dotenv()
loginManager.login_view = 'login'


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
    latest_post = Post.query.order_by(desc(Post.post_id)).first()
    embeds = [post.link.split('/')[-1] for post in all_posts]
    if current_user.is_authenticated:
        username = current_user.username
    else: 
        username = 'Anonymous'
    return render_template('home.html', all_posts=all_posts, latest_post=latest_post, embeds=embeds, username=username)

@app.get('/post/new')
def create_post_form():
    return render_template('create_post.html')

@app.post('/post/new')
def create_post():
    if not current_user.is_authenticated:
        flash('You need to log in to create a new post', 'danger')
        return redirect(url_for('login'))
    title = request.form.get('title')
    body = request.form.get('body')
    link = request.form.get('link')
    new_post = Post(title=title, body=body, link=link, username=current_user.username)
    db.session.add(new_post)
    db.session.commit()
    
    return redirect('/')
    
@app.route('/about')
def about():
    return render_template('about.html', title='About Us')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You\'re already logged in!', 'success')
        return redirect('/')
    form = RegistrationForm()
    if form.validate_on_submit():
        hashedPass = bcrypt.generate_password_hash(form.confirm_password.data).decode('utf8')
        newUser = Users(username = form.username.data, password = hashedPass)
        db.session.add(newUser)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('profile'))
    return render_template('register.html', title='register', form=form)

@loginManager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if(current_user.is_authenticated):
        flash('You\'re already logged in!', 'success')
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('You have been logged in!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(('home'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', title='login', form=form)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        if(form.password.data != ''):
            hashedPass = bcrypt.generate_password_hash(form.confirm_password.data).decode('utf8')
            current_user.password = hashedPass
        current_user.username = form.username.data
        current_user.firstname = form.firstname.data
        current_user.lastname = form.lastname.data
        db.session.commit()
        flash(f'Account updated!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname
    token = session.get(TOKEN_INFO, None)
    return render_template('profile.html', title='profile', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect('login')

@app.route("/spotifylogin")
def spotifylogin():
    authUrl = create_spotify_oauth().get_authorize_url()
    return redirect(authUrl)

@app.route('/spotifyredirect')
def spotifyRedirect():
    session.clear()
    code = request.args.get('code')
    session[TOKEN_INFO] =  create_spotify_oauth().get_access_token(code)
    try:
        token_info = get_token()
    except:
        flash('not logged in', 'danger')
        redirect(url_for('login'))
    sp = spotipy.Spotify(auth=token_info['access_token'])
    userId = sp.me()['id']
    
    existUser = Users.query.filter_by(username=userId).first()
    if(existUser):
        login_user(existUser, True)
        current_user.username = userId
        next_page = request.args.get('next')
        flash('You have been logged in!', 'success')
        return redirect(next_page) if next_page else redirect(('profile'))
    else:
        hashedPass = bcrypt.generate_password_hash("temp").decode('utf8')
        newUser = Users(username = userId, password = hashedPass)
        db.session.add(newUser)
        db.session.commit()
        current_user.username = userId
        flash(f'Account {userId}! CHANGE YOUR PASSWORD NOW', 'danger')
        return redirect(('profile'))
    # return redirect(url_for('profile',_external=True))

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
    
def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        redirect(url_for('login', _external=False))
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if(is_expired):
        redirect(url_for('login', _external=True))
        # spotify_oauth = create_spotify_oauth()
        # token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])

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

@app.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)

    comment_text = request.form.get('comment')

    if not comment_text:
        flash('Comment cannot be empty', 'error')
        return redirect(url_for('get_single_post', post_id=post_id))

    new_comment = Comment(comment=comment_text, user_id=current_user.id, post_id=post_id)
    db.session.add(new_comment)
    db.session.commit()

    flash('Comment added successfully', 'success')
    return redirect(url_for('get_single_post', post_id=post_id))


@app.get('/post/<int:post_id>')
def get_single_post(post_id):
    single_post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id).all()
    embed_parts = single_post.link.split('/')
    embed = embed_parts[-1]
    return render_template('single_post.html', post=single_post, comments=comments, embed=embed)

if __name__ == '__main__':
	app.run(debug=True)

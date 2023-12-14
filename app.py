from flask import Flask, render_template, request, redirect, flash, url_for, session
from src.models import db, Post, Users, Comment, Like
from dotenv import load_dotenv
import os
from forms import RegistrationForm, LoginForm, SearchForm, EditProfileForm
from spotipy.oauth2 import SpotifyOAuth
import spotipy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from sqlalchemy import desc
from sqlalchemy.orm import joinedload
import time
from sqlalchemy.orm import relationship
from sqlalchemy import func


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
    all_users = Users.query.all()
    latest_post = Post.query.order_by(desc(Post.post_id)).first()
    
    # Get the number of likes for each post using SQLAlchemy's func.count
    like_counts = db.session.query(Post.post_id, func.sum(Post.likes)).group_by(Post.post_id).all()
    like_counts = dict(like_counts)

    # Post with most likes
    most_liked_post = Post.query.order_by(desc(Post.likes)).first()
    best_embed = most_liked_post.link.split('/')[-1]

    # Extract the last part of the link for embedding
    embeds = [post.link.split('/')[-1] for post in reversed(all_posts)] 

    if current_user.is_authenticated:
        username = current_user.username
        userid = current_user.id
    else: 
        username = 'Anonymous'
        userid = None
    
    return render_template('home.html', all_users=all_users, all_posts=all_posts, latest_post=latest_post, embeds=embeds, username=username, userid=userid, like_counts=like_counts, most_liked_post=most_liked_post, best_embed = best_embed)

@app.get('/post/new')
@login_required
def create_post_form():
    return render_template('create_post.html')

@app.post('/post/new')
@login_required
def create_post():
    if not current_user.is_authenticated:
        flash('You need to log in to create a new post', 'danger')
        return redirect(url_for('login'))
    title = request.form.get('title')
    body = request.form.get('body')
    link = request.form.get('link')
    userid = Users.query.filter_by(username=current_user.username).first()
    new_post = Post(title=title, body=body, link=link, userid=userid.id)
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
        newUser = Users(username=form.username.data, password=hashedPass)
        db.session.add(newUser)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect('/')  # Redirect to the homepage after successful signup

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
        user = Users.query.filter_by(username=form.username.data).first()
        if(user is not None):
            if (user.id == current_user.id):
                if(form.password.data != ''):
                    hashedPass = bcrypt.generate_password_hash(form.confirm_password.data).decode('utf8')
                    current_user.password = hashedPass
                current_user.firstname = form.firstname.data
                current_user.lastname = form.lastname.data
                db.session.commit()
                flash(f'Account updated!', 'success')
                return redirect(url_for('profile'))
            else:
                flash('Invalid username', 'danger')
                return redirect(url_for('profile'))
        else:
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
        # if(current_user.spotify_id is not None):
        if(current_user.spotify_id):
            form.spotifyid.data = current_user.spotify_id
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
    session[TOKEN_INFO] = create_spotify_oauth().get_access_token(code)
    try:
        token_info = get_token()
    except:
        flash('not logged in', 'danger')
        redirect(url_for('login'))
    sp = spotipy.Spotify(auth=token_info['access_token'])
    userId = sp.me()['id']
    
    existUser = Users.query.filter_by(spotify_id=userId).first()
    if(existUser):
        login_user(existUser, True)
        current_user.username = userId
        next_page = request.args.get('next')
        flash('You have been logged in!', 'success')
        return redirect(next_page) if next_page else redirect(('profile'))
    else:
        flash(f'User does not exist, create account first', 'danger')
        return redirect(('spotifyredirectsignup'))
    # return redirect(url_for('profile',_external=True))

@app.route('/spotifyredirectsignup', methods=['GET', 'POST'])
def spotifyRedirectSignup():
    form = RegistrationForm()
    code = request.args.get('code')
    session[TOKEN_INFO] =  create_spotify_oauth().get_access_token(code)
    try:
        token_info = get_token()
    except:
        flash('not logged in', 'danger')
        redirect(url_for('spotifylogin'))
    sp = spotipy.Spotify(auth=token_info['access_token'])
    userId = sp.me()['id']

    if form.validate_on_submit():
        hashedPass = bcrypt.generate_password_hash(form.confirm_password.data).decode('utf8')
        newUser = Users(username = form.username.data, password = hashedPass, spotify_id = userId)
        db.session.add(newUser)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('profile'))
    return render_template('registerspotify.html', title='registerspotify', form=form)


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
			posts = posts.order_by(Post.title).all()
			return render_template("search.html", form = form, searched = Post.searched, posts = posts)
		else:
			error = "Cant search nothing"
			return redirect(('home'))
	# Return a response
	return render_template("search.html", form=form)
    
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

    new_comment = Comment(comment=comment_text, id=current_user.id, post_id=post_id)
    db.session.add(new_comment)
    db.session.commit()

    flash('Comment added successfully', 'success')
    return redirect(url_for('get_single_post', post_id=post_id))




@app.get('/post/<int:post_id>')
def get_single_post(post_id):
    all_users = Users.query.all()
    single_post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id).all()
    embed_parts = single_post.link.split('/')
    embed = embed_parts[-1]
    return render_template('single_post.html', post=single_post, comments=comments, embed=embed, all_users=all_users)

@app.route('/profile/delete', methods=['GET', 'POST'])
@login_required
def delete_profile():
    if request.method == 'POST':
        # Delete the users posts first
        posts_to_delete = Post.query.filter_by(userid=current_user.id).all()
        for post in posts_to_delete:
            db.session.delete(post)
        
        # Delete user account
        db.session.delete(current_user)
        db.session.commit()
        flash('Your account has been deleted!', 'success')
        return redirect(url_for('logout'))

    return render_template('delete_profile.html', title='Delete Profile')

@app.route('/comment/delete/<int:comment_id>')
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get(comment_id)

    # For when the comment doesn't exist, but that shouldn't happen
    if not comment:
        flash('Comment not found', 'danger')
        return redirect(url_for('index'))

    # Check if the current logged in user is the same as the one who made the comment
    if current_user.is_authenticated and current_user.id == comment.id:
        db.session.delete(comment)
        db.session.commit()
        flash('Comment deleted successfully', 'success')
    else:
        flash('You do not have permission to delete this comment', 'danger')

    return redirect(url_for('get_single_post', post_id=comment.post_id))

@app.route('/comment/edit/<int:comment_id>', methods=['GET', 'POST'])
@login_required
def edit_comment(comment_id):
    comment = Comment.query.get(comment_id)

    if not comment:
        flash('Comment not found', 'danger')
        return redirect(url_for('get_single_post', post_id=comment.post_id))

    if request.method == 'POST':
        comment.comment = request.form.get('edited_comment')
        db.session.commit()
        flash('Comment updated successfully', 'success')
        return redirect(url_for('get_single_post', post_id=comment.post_id))

    return redirect(url_for('get_single_post', post_id=comment.post_id))

@app.route('/like_post/<int:post_id>', methods=['GET'])
@login_required
def like_post(post_id):
    post = Post.query.get(post_id)
    
    if post is None:
        return redirect(url_for('index'))
    
    liked_by_list = post.liked_by.split(',') if post.liked_by else []
    
    if str(current_user.id) in liked_by_list:
        liked_by_list.remove(str(current_user.id))
        post.likes -= 1
    else:
        liked_by_list.append(str(current_user.id))
        post.likes += 1
    
    post.liked_by = ','.join(liked_by_list)
    db.session.commit()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
	app.run(debug=True)

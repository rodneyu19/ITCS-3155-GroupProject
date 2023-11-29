from flask import Flask, render_template, request, redirect, url_for
from src.models import db, Post, Comment
from auth import spotify_bp
from flask import session
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()

if None in (os.getenv("DB_USER"), os.getenv("DB_PASS"), os.getenv("DB_HOST"), os.getenv("DB_PORT"), os.getenv("DB_NAME")):
    raise ValueError("Fix the variables in your .env lmao")

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = \
    f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASS")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}'

# Register Spotify blueprint from auth.py
app.register_blueprint(spotify_bp, url_prefix="/spotify_login")

db.init_app(app)

# Routes and other parts of your application...

# Routes
@app.route('/')
def index():
    all_posts = Post.query.all()
    return render_template('home.html', all_posts=all_posts)

@app.route('/post/<spotify_id>')
def view_post(spotify_id):
    post = Post.query.filter_by(spotify_id=spotify_id).first()

    if post is None:
        print(f"No post found for spotify_id: {spotify_id}")
        return "Post not found"

    comments = Comment.query.filter_by(post_id=post.id).all()
    return render_template('view_post.html', post=post, comments=comments)

@app.route('/post/<spotify_id>/comment', methods=['POST'])
def add_comment(spotify_id):
    post = Post.query.filter_by(spotify_id=spotify_id).first()

    if post is None:
        print(f"No post found for spotify_id: {spotify_id}")
        return "Post not found"

    comment_text = request.form.get('comment')
    new_comment = Comment(comment_text=comment_text, post_id=post.id)
    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for('view_post', spotify_id=spotify_id))

@app.route('/post/new', methods=['GET', 'POST'])
def create_post_form():
    if request.method == 'GET':
        return render_template('create_post.html')
    elif request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        new_post = Post(title=title, body=body)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/')

@app.route("/logout")
def logout():
    if "spotify_oauth" in session:
        del session["spotify_oauth"]
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
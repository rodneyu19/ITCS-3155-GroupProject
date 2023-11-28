from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from src.models import db, Post, Comment

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'  # Replace with your database URI
db.init_app(app)

# Spotify credentials setup
client_credentials_manager = SpotifyClientCredentials(client_id=os.getenv("SPOTIFY_CLIENT_ID"),
client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"))
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

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


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

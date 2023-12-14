from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import Column, Integer


db = SQLAlchemy()

# @loginManager.user_loader
# def load_user(user_id):
#     return Users.query.get(int(user_id))



class Post(db.Model):
    post_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(255))
    userid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    likes = db.Column(db.Integer, default=0)
    liked_by = db.Column(db.String(255), default='')  # Storing user IDs who liked the post as a string
    
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(16), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    firstname = db.Column(db.String(16))
    lastname = db.Column(db.String(16))
    spotify_id = db.Column(db.String(16))

class Comment(db.Model):
    __tablename__ = 'comments'

    comment_id = db.Column(db.Integer, primary_key=True)  # Define the primary key column
    comment = db.Column(db.String(255))

    id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('Users', backref='user_comments')

    post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'))
    post = db.relationship('Post', backref='post_comments')

class Like(db.Model):
    __tablename__ = 'likes'
    like_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'))
 
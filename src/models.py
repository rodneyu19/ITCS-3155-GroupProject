from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    spotify_id = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    title = db.Column(db.String(100))
    body = db.Column(db.Text)
    spotify_link = db.Column(db.String(255))  


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    comment_text = db.Column(db.Text)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def __init__(self, comment_text, post_id):
        self.comment_text = comment_text
        self.post_id = post_id


from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'YOUR_DATABASE_URI'
db = SQLAlchemy(app)

class Post(db.Model):
    __tablename__ = 'post'
    post_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    spotify_link = db.Column(db.String(255), nullable=False)
    comments = db.relationship('Comment', backref='post', lazy=True)

class Comment(db.Model):
    __tablename__ = 'comments'
    comment_id = db.Column(db.Integer, primary_key=True)
    comment_text = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'), nullable=False)

def add_comment(post_id):
    post = Post.query.get_or_404(post_id)

    comment_text = request.form.get('comment')

    new_comment = Comment(**comment_text)
    db.session.add(new_comment)
    db.session.commit()

    return redirect(url_for('view_post', post_id=post_id))

@app.route('/post/create', methods=['POST'])
def create_post():
    post_data = {
        'title': request.form.get('title'),
        'body': request.form.get('body'),
        'spotify_link': request.form.get('spotify_link')
    }

    new_post = Post(**post_data)
    db.session.add(new_post)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/post/<int:post_id>')
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    comments = post.comments
    return render_template('view_post.html', post=post, comments=comments)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

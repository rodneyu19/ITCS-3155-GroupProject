from flask import Flask, render_template, request, redirect
from src.models import db, Post
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()

if None in (os.getenv("DB_USER"), os.getenv("DB_PASS"), os.getenv("DB_HOST"), os.getenv("DB_PORT"), os.getenv("DB_NAME")):
    raise ValueError("Fix the variables in your .env lmao")

app.config['SQLALCHEMY_DATABASE_URI'] = \
    f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASS")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}'

db.init_app(app)

@app.get('/')
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


from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.get('/')
def index():
    return render_template('home.html')

@app.get('/post/new')
def create_post_form():
    return render_template('create_post.html')
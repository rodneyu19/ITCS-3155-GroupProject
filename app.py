from flask import Flask, render_template, request, redirect, flash, url_for
from src.models import db, Post
from dotenv import load_dotenv
from forms import SearchForm
import os

app = Flask(__name__)

load_dotenv()

if None in (os.getenv("DB_USER"), os.getenv("DB_PASS"), os.getenv("DB_HOST"), os.getenv("DB_PORT"), os.getenv("DB_NAME")):
    raise ValueError("Fix the variables in your .env lmao")

app.config['SQLALCHEMY_DATABASE_URI'] = \
    f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASS")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}'

db.init_app(app)

@app.get('/')
@app.get('/home')
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
    
# Pass though Navbar
@app.context_processor
def base():
	form = SearchForm()
	return dict(form=form)

# Search Funciton
@app.route('/search', methods=['POST'])
def search():
	forms = SearchForm()
	posts = Posts.query
	if form.validate_on_submit():
		# Get data from submitted form
		post.searched = form.searched.data
		# Query the Database
		posts = posts.filter(Posts.body.like('%' + post.searched + '%'))
		posts = post.order_by(Posts.title).all()
		
		return render_template("search.html", 
								form = form, 
								searched = post.searched,
								posts = posts)
	
if __name__ == '__main__':
	app.run(debug=True)

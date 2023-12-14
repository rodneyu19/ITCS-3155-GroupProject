import unittest
from flask import Flask, url_for
from src.models import db, Post, Users
from flask import Flask
from flask_login import current_user
from app import  db
from src.models import Users

def create_app(testing=True):
	app = Flask(__name__)

	# Set the testing config
	app.config['TESTING'] = testing
	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

	# Initialize the test database
	with app.app_context():
		db.init_app(app)
		db.create_all()

	return app

class AppTesting(unittest.TestCase):
	
	def setUp(self):
		# Create a test app
		self.app = create_app(testing=True)
		self.app_context = self.app.app_context()
		self.app_context.push()

		# Create a test client
		self.client = self.app.test_client()

		# Create the test database schema
		with self.app.app_context():
			db.create_all()
	
	def tearDown(self):
		# Remove the test database
		with self.app.app_context():
			db.session.remove()
			db.drop_all()

		self.app_context.pop()

	# Test the index route
	def test_index_route(self):
		response = self.client.get('/')
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'Welcome to the Home Page', response.data)
        
	# Test home route
	def test_home_route(self):
		response = self.client.get('/home')
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'Welcome to the Home Page', response.data)

	# Test create post route
	def test_create_post_route(self):
		response = self.client.get('/post/new')
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'Create Post', response.data)

		response = self.client.post('/post/new', data={'title': 'Test Title', 'body': 'Test Body', 'link': 'Test Link'})
		self.assertEqual(response.status_code, 302)

	# Test register()
	def test_register_route(self):
		response = self.client.get('/register')
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'Register', response.data)

	# Test the login()
	def test_login_route(self):
		response = self.client.get('/login')
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'Login', response.data)

	# Test search()
	def test_search_route(self):
		response = self.client.post(url_for('search'), data={'searched': 'your_search_term'})
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'Search Results', response.data)

	# Test delete_post()
	def test_delete_post_route(self):
		# have a post with ID=1 for testing
		response = self.client.get(url_for('delete_post', post_id=1))
		self.assertEqual(response.status_code, 302)
	def test_register_user(self):
        response = self.client.post('/register', data=dict(
            username='testuser',
            password='testpassword',
            confirm_password='testpassword'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        user = Users.query.filter_by(username='testuser').first()
        self.assertIsNotNone(user)
	def test_login_user(self):
        # Assuming you have registered a test user before
        test_user = Users(username='testuser', password='testpassword')
        db.session.add(test_user)
        db.session.commit()

        response = self.client.post('/login', data=dict(
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(current_user.is_authenticated)
	def test_login_with_wrong_credentials(self):
        response = self.client.post('/login', data=dict(
            username='wronguser',
            password='wrongpassword'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(current_user.is_authenticated)
        
	def test_edit_profile(self):
        # Assuming you have a logged-in user
        test_user = Users(username='testuser', password='testpassword')
        db.session.add(test_user)
        db.session.commit()

        with self.client:
            self.client.post('/login', data=dict(
                username='testuser',
                password='testpassword'
            ), follow_redirects=True)

            response = self.client.post('/profile/edit', data=dict(
                username='newusername',
                firstname='New',
                lastname='User',
                password='newpassword',
                confirm_password='newpassword'
            ), follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            user = Users.query.filter_by(username='newusername').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.firstname, 'New')
            self.assertEqual(user.lastname, 'User')
	'''
	# Test edit_post()
	def test_edit_post_route(self):
		# Have a post with ID=1 for testing
		response = self.client.get(url_for('edit_post', post_id=1))
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'Edit Post', response.data)

		# Have a form with title, body, and link fields
		response = self.client.post(url_for('edit_post', post_id=1), data={'title': 'New Title', 'body': 'New Body', 'link': 'New Link'})
		self.assertEqual(response.status_code, 302)
	'''

	# Test logout()
	def test_logout_route(self):
		response = self.client.get(url_for('logout'))
		self.assertEqual(response.status_code, 302)

	# Test spotifylogin()
	def test_spotifylogin_route(self):
		response = self.client.get(url_for('spotifylogin'))
		self.assertEqual(response.status_code, 302)

	'''
	# Test profile()
	def test_profile_route(self):
		response = self.client.get(url_for('profile'))
		self.assertEqual(response.status_code, 302)  # Assuming you redirect if not logged in

		# Log in before testing the profile route
		self.client.post(url_for('login'), data={'username': 'your_username', 'password': 'your_password', 'remember': False})

		response = self.client.get(url_for('profile'))
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'Your Profile', response.data)
	'''
 
	

if __name__ == '__main__':
    unittest.main()

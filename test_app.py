import unittest
from flask import Flask, url_for
from src.models import db, Post, Users

class AppTesting(unittest.TestCase):
	
	ef setUp(self):
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
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to the Home Page', response.data)
        
	# Test home route
	def test_home_route(self):
		response = self.app.get('/home')
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'Welcome to the Home Page', response.data)

	# Test create post route
	def test_create_post_route(self):
		response = self.app.get('/post/new')
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'Create Post', response.data)

		response = self.app.post('/post/new', data={'title': 'Test Title', 'body': 'Test Body', 'link': 'Test Link'})
		self.assertEqual(response.status_code, 302) 

	# Test register()
    def test_register_route(self):
        response = self.app.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)

	# Test the login()
    def test_login_route(self):
        response = self.app.get('/login')
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

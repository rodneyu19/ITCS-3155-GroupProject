import pytest
from app import app as flask_app

@pytest.fixture
def app():
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_home_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Top Post' in response.data 

def test_registration_route(client):
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Register' in response.data  

def test_login_route(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data  

def test_logout_route(client):
    response = client.get('/logout')
    assert response.status_code == 302 

def test_post_creation(client):
    with client:
        client.post('/login', data=dict(username='test_user', password='test_password'))

        response = client.post('/post/new', data=dict(
            title='Test Post Title',
            body='Test Post Body',
            link='https://example.com'
        ), follow_redirects=True)

        
        assert response.status_code == 200 
        assert b'Test Post Title' in response.data

        

def test_profile_route(client):
    response = client.get('/profile')
    assert response.status_code == 302
    assert b'Edit Profile' in response.data 

def test_search_route(client):
    response = client.post('/search', data=dict(searched='test_query'))
    assert response.status_code == 200
    assert b'You searched for' in response.data  

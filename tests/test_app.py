import pytest
from app import app

def test_index_route():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200


def test_blog_route():
    client = app.test_client()
    response = client.get('/blog')
    assert response.status_code == 200


def test_contact_route():
    client = app.test_client()
    response = client.get('/contact')
    assert response.status_code == 200


def test_portal_requires_auth_redirect():
    client = app.test_client()
    response = client.get('/portal')
    assert response.status_code == 302
    assert '/login' in response.headers.get('Location', '')


def test_portal_authenticated_success():
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['user'] = {
            'name': 'Test User',
            'email': 'test@example.com',
            'id': 'test-id'
        }
    response = client.get('/portal')
    assert response.status_code == 200


def test_portal_profile_authenticated_success():
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['user'] = {
            'name': 'Test User',
            'email': 'test@example.com',
            'id': 'test-id'
        }
    response = client.get('/portal/profile')
    assert response.status_code == 200

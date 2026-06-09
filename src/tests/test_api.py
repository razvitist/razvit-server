import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

token = ''
headers={}

def auth_token(username: str, password: str):
  response = client.post(
    '/auth/token', 
    data={'username': username, 'password': password}
  )
  return response

def auth_change_password(old_password: str, new_password: str):
  response = client.post(
    '/auth/change-password', 
    json={'old_password': old_password, 'new_password': new_password},
    headers=headers
  )
  return response

def test_auth():
  try:
    response = auth_token('testuser', 'testpass')
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    response = client.delete(
      '/auth/delete',
      headers=headers
    )
  except:
    ...
  try:
    response = auth_token('testuser', 'testpass1')
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    response = client.delete(
      '/auth/delete',
      headers=headers
    )
  except:
    ...
  response = client.post(
    '/auth',
    json={'username': 'testuser', 'email': 'testemail', 'password': 'testpass'}
  )
  assert response.status_code == 200
  assert response.json()['created'] == 'testuser'
  response = client.post(
    '/auth',
    json={'username': 'testuser', 'email': 'testemail', 'password': 'testpass'}
  )
  assert response.json() == {'already exist': 'testuser'}

def test_auth_token():
  global token, headers
  response = auth_token('testuser', 'testpass')
  assert response.status_code == 200
  assert 'access_token' in response.json()
  assert response.json()['token_type'] == 'bearer'
  token = response.json()['access_token']
  headers = {'Authorization': f'Bearer {token}'}

def test_auth_change_password():
  response = auth_change_password('testpass', 'testpass1')
  assert response.status_code == 200
  assert response.json() == {'detail': 'Password changed successfully'}
  response = auth_token('testuser', 'testpass')
  assert response.json() == {'detail': 'Unauthorized'}
  response = auth_token('testuser', 'testpass1')
  assert 'access_token' in response.json()
  response = auth_change_password('testpass', 'testpass')
  assert response.json() == {'detail': 'Old password is incorrect'}
  response = auth_change_password('testpass1', 'testpass')
  assert response.json() == {'detail': 'Password changed successfully'}

def test_youtube():
  data = {
    "channel": "https://www.youtube.com/channel/UCFxwS8HIGH5_ut1fk0PNAHw",
    "lang": "en",
    "tags": "FastAPI"
  }
  response = client.post(
    '/youtube/add', 
    data=data,
    headers=headers
  )
  assert response.status_code == 200

  response = client.get('/youtube/UCFxwS8HIGH5_ut1fk0PNAHw')
  assert response.status_code == 200

  response = client.get('/youtube/channels.json')
  assert response.status_code == 200
  assert response.json()[-1]['url'] == 'https://www.youtube.com/channel/UCFxwS8HIGH5_ut1fk0PNAHw'
  assert response.json()[-1]['lang'] == 'en'
  assert response.json()[-1]['tags'] == ['FastAPI']

def test_band():
  response = client.post(
    '/apikey',
    headers=headers
  )
  assert response.status_code == 200
  assert 'apikey' in response.json()
  apikey = response.json()['apikey']
  response = client.get(f'/set/{apikey}/test/1')
  assert response.json() == {'pin': 'test', 'val': 1}
  response = client.get(f'/plus/{apikey}/test/1')
  assert response.json() == {'pin': 'test', 'plus': 1}
  response = client.get(f'/get/{apikey}/test')
  assert response.text == '2'
  response = client.get(f'/get/{apikey}')
  assert 'test' in response.json()
  response = client.get(f'/del/{apikey}/test')
  assert response.json() == {'deleted': 'test'}
  response = client.get(f'/get/{apikey}')
  assert 'test' not in response.json()
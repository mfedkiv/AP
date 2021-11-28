import json
import pytest
from models.table_models import *
from app import app

user1 = User(username="user1", name="name1", surname="surname1", password="pass1")
user2 = User(username="user2", name="name2", surname="surname2", password="pass2")


def test_register_user():
    client = app.test_client()
    url = "http://127.0.0.1:5000/register"

    user_data_json = "{\n    \"name\" : \"Name\",\n    \"surname\": \"Surname\",\n    \"username\": " \
                     "\"username\",\n    \"password\": \"pass\" \n} "
    headers = {
        'Content-Type': 'application/json'
    }
    resp = client.post(url, headers=headers, data=user_data_json)

    user = session.query(User).filter_by(username="username").first()
    assert resp.status_code == 200
    assert user.name == "Name"

    resp = client.post(url, headers=headers, data=user_data_json)
    assert resp.status_code == 406

    session.delete(user)
    session.commit()


@pytest.fixture(scope="module")
def create_user():
    user = User(name="name", surname="surname", username="username", password="pass")
    session.add(user)
    session.commit()
    yield
    session.delete(user)
    session.commit()


def test_login_user(create_user):
    client = app.test_client()
    url = "http://127.0.0.1:5000/login"

    login_data_json = "{\n    \"username\": \"username\",\n   \"password\": \"pass\" \n} "

    non_existing_user_json = "{\n    \"username\": \"invalid\",\n   \"password\": \"pass\" \n} "

    not_matching_password_json = "{\n    \"username\": \"username\",\n   \"password\": \"invalid\" \n} "

    headers = {
        'Content-Type': 'application/json'
    }
    resp = client.post(url, headers=headers, data=login_data_json)

    assert resp.status_code == 200

    resp = client.post(url, headers=headers, data=non_existing_user_json)

    assert resp.status_code == 404

    resp = client.post(url, headers=headers, data=not_matching_password_json)

    assert resp.status_code == 406


@pytest.fixture()
def login_user(create_user):
    login_data_json = "{\n    \"username\": \"username\",\n   \"password\": \"pass\" \n} "
    test_client = app.test_client()
    url = 'http://127.0.0.1:5000/login'
    headers = {
        'Content-Type': 'application/json'
    }
    resp = test_client.post(url, headers=headers, data=login_data_json)
    access_token_data_json = json.loads(resp.get_data(as_text=True))
    return access_token_data_json


def test_logout_user(login_user):
    token = login_user["access_token"]
    client = app.test_client()
    url = "http://127.0.0.1:5000/logout"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    }
    resp = client.delete(url, headers=headers)

    black_listed_token = session.query(TokenBlockList).filter_by(jti=token).first
    assert resp.status_code == 200
    assert black_listed_token

    session.query(TokenBlockList).delete()
    session.commit()


@pytest.fixture(scope="module")
def get_access_token_two_users():
    client = app.test_client()
    headers = {
        'Content-Type': 'application/json'
    }

    session.add(user1)
    session.add(user2)
    session.commit()
    calendar1 = Calendar(title="user1's calendar", user_id=user1.id)
    calendar2 = Calendar(title="user2's calendar", user_id=user2.id)
    session.add(calendar1)
    session.add(calendar2)
    session.commit()
    user = session.query(User).filter_by(username=user1.username).first()
    event = Event(title="title", date='2021-12-01', owner=user.id)
    session.add(event)
    session.commit()
    user1_login_data = "{\n    \"username\": " \
                       "\"user1\",\n    \"password\": \"pass1\" \n} "
    user2_login_data = "{\n    \"username\": " \
                       "\"user2\",\n    \"password\": \"pass2\" \n} "
    resp1 = client.post("/login", headers=headers, data=user1_login_data)
    resp2 = client.post("/login", headers=headers, data=user2_login_data)
    yield [json.loads(resp1.get_data(as_text=True)), json.loads(resp2.get_data(as_text=True))]
    session.query(CalendarEvents).delete()
    session.query(EventUsers).delete()
    session.commit()
    session.delete(calendar1)
    session.delete(calendar2)
    session.commit()
    session.delete(event)
    session.commit()
    session.delete(user1)
    session.delete(user2)
    session.commit()


def test_user_get(get_access_token_two_users):
    client = app.test_client()
    token1 = get_access_token_two_users[0]['access_token']
    token2 = get_access_token_two_users[1]['access_token']
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token1
    }
    invalid_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token2
    }
    user = session.query(User).filter_by(username=user1.username).first()
    url = "http://127.0.0.1:5000/user/" + str(user.id)
    invalid_url = "http://127.0.0.1:5000/user/10000"
    resp = client.get(url, headers=headers)
    assert resp.status_code == 200
    resp = client.get(invalid_url, headers=headers)
    assert resp.status_code == 404
    resp = client.get(url, headers=invalid_headers)
    assert resp.status_code == 403


def test_user_update(get_access_token_two_users):
    client = app.test_client()
    token1 = get_access_token_two_users[0]['access_token']
    token2 = get_access_token_two_users[1]['access_token']
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token1
    }
    invalid_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token2
    }
    json_update_user = "{\n    \"name\" : \"new_name1\",\n    \"surname\": \"new_surname1\",\n    \"username\": " \
                       "\"user1\" \n  } "
    invalid_json_update_user = "{\n    \"name\" : \"new_name1\",\n    \"surname\": \"new_surname1\",\n    \"username\": " \
                               "\"user2\" \n } "
    user = session.query(User).filter_by(username=user1.username).first()
    url = "http://127.0.0.1:5000/user/" + str(user.id)
    invalid_url = "http://127.0.0.1:5000/user/10000"
    resp = client.put(url, headers=headers, data=json_update_user)
    assert resp.status_code == 200
    resp = client.put(invalid_url, headers=headers, data=json_update_user)
    assert resp.status_code == 404
    resp = client.put(url, headers=invalid_headers, data=json_update_user)
    assert resp.status_code == 403
    resp = client.put(url, headers=headers, data=invalid_json_update_user)
    assert resp.status_code == 400


def test_user_get_events(get_access_token_two_users):
    client = app.test_client()
    token1 = get_access_token_two_users[0]['access_token']
    token2 = get_access_token_two_users[1]['access_token']
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token1
    }
    invalid_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token2
    }
    url = "http://127.0.0.1:5000/user/events/" + user1.username
    invalid_url = "http://127.0.0.1:5000/user/events/invalid"
    resp = client.get(url, headers=headers)
    assert resp.status_code == 200
    resp = client.get(invalid_url, headers=headers)
    assert resp.status_code == 400
    resp = client.get(url, headers=invalid_headers)
    assert resp.status_code == 403


def test_add_user_to_event(get_access_token_two_users):
    client = app.test_client()
    token1 = get_access_token_two_users[0]['access_token']
    token2 = get_access_token_two_users[1]['access_token']
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token1
    }
    invalid_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token2
    }
    user = session.query(User).filter_by(username=user1.username).first()
    event = session.query(Event).filter_by(owner=user.id).first()
    url = "http://127.0.0.1:5000/user/add_user_to_event/" + str(user.id) + "/" + str(event.id)
    invalid_user_url = "http://127.0.0.1:5000/user/add_user_to_event/10000" + "/" + str(event.id)
    invalid_event_url = "http://127.0.0.1:5000/user/add_user_to_event/" + str(user.id) + "/10000"
    resp = client.post(url, headers=headers)
    assert resp.status_code == 200
    resp = client.post(invalid_user_url, headers=headers)
    assert resp.status_code == 404
    resp = client.post(invalid_event_url, headers=headers)
    assert resp.status_code == 404
    resp = client.post(url, headers=invalid_headers)
    assert resp.status_code == 403


def test_calendar_get(get_access_token_two_users):
    client = app.test_client()

    token1 = get_access_token_two_users[0]['access_token']
    token2 = get_access_token_two_users[1]['access_token']
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token1
    }
    invalid_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token2
    }
    user = session.query(User).filter_by(username=user1.username).first()
    calendar = session.query(Calendar).filter_by(user_id=user.id).first()
    url = "http://127.0.0.1:5000/calendars/" + str(calendar.id)
    invalid_url = "http://127.0.0.1:5000/calendars/10000"
    resp = client.get(url, headers=headers)
    assert resp.status_code == 200
    resp = client.get(invalid_url, headers=headers)
    assert resp.status_code == 400
    resp = client.get(url, headers=invalid_headers)
    assert resp.status_code == 403


def test_calendar_update(get_access_token_two_users):
    client = app.test_client()
    token1 = get_access_token_two_users[0]['access_token']
    token2 = get_access_token_two_users[1]['access_token']
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token1
    }
    invalid_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token2
    }
    json_update_calendar = "{\n  \"title\" : \"new user1's calendar\" \n  } "
    user = session.query(User).filter_by(username=user1.username).first()
    calendar = session.query(Calendar).filter_by(user_id=user.id).first()
    url = "http://127.0.0.1:5000/calendars/" + str(calendar.id)
    invalid_url = "http://127.0.0.1:5000/calendars/10000"
    resp = client.put(url, headers=headers, data=json_update_calendar)
    assert resp.status_code == 200
    resp = client.put(invalid_url, headers=headers, data=json_update_calendar)
    assert resp.status_code == 400
    resp = client.put(url, headers=invalid_headers, data=json_update_calendar)
    assert resp.status_code == 403


def test_event_get(get_access_token_two_users):
    client = app.test_client()
    token1 = get_access_token_two_users[0]['access_token']
    token2 = get_access_token_two_users[1]['access_token']
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token1
    }
    invalid_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token2
    }
    user = session.query(User).filter_by(username=user1.username).first()
    event = session.query(Event).filter_by(owner=user.id).first()
    url = "http://127.0.0.1:5000/event/" + str(event.id)
    invalid_url = "http://127.0.0.1:5000/event/10000"
    resp = client.get(url, headers=headers)
    assert resp.status_code == 200
    resp = client.get(invalid_url, headers=headers)
    assert resp.status_code == 404
    resp = client.get(url, headers=invalid_headers)
    assert resp.status_code == 200


def test_event_update(get_access_token_two_users):
    client = app.test_client()
    token1 = get_access_token_two_users[0]['access_token']
    token2 = get_access_token_two_users[1]['access_token']
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token1
    }
    invalid_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token2
    }
    json_update_event = "{\n  \"title\" : \"new event title\" \n} "
    user = session.query(User).filter_by(username=user1.username).first()
    event = session.query(Event).filter_by(owner=user.id).first()
    url = "http://127.0.0.1:5000/event/" + str(event.id)
    invalid_url = "http://127.0.0.1:5000/event/10000"
    resp = client.put(url, headers=headers, data=json_update_event)
    assert resp.status_code == 200
    resp = client.put(invalid_url, headers=headers, data=json_update_event)
    assert resp.status_code == 400
    resp = client.put(url, headers=invalid_headers, data=json_update_event)
    assert resp.status_code == 403


@pytest.fixture()
def add_event():
    user = session.query(User).filter_by(username=user1.username).first()
    event = Event(title="event", date='2021-12-01', owner=user.id)
    session.add(event)
    session.commit()


def test_event_delete(get_access_token_two_users, add_event):
    client = app.test_client()
    token1 = get_access_token_two_users[0]['access_token']
    token2 = get_access_token_two_users[1]['access_token']
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token1
    }
    invalid_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token2
    }
    user = session.query(User).filter_by(username=user1.username).first()
    event = session.query(Event).filter_by(owner=user.id, title="event").first()
    url = "http://127.0.0.1:5000/event/" + str(event.id)
    invalid_url = "http://127.0.0.1:5000/event/10000"
    resp = client.delete(url, headers=headers)
    assert resp.status_code == 204
    resp = client.delete(invalid_url, headers=headers)
    assert resp.status_code == 400
    resp = client.delete(url, headers=invalid_headers)
    assert resp.status_code == 400


def test_events_get_by_calendar(get_access_token_two_users):
    session.add(user1)
    client = app.test_client()
    token1 = get_access_token_two_users[0]['access_token']
    token2 = get_access_token_two_users[1]['access_token']
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token1
    }
    invalid_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token2
    }
    user = session.query(User).filter_by(username=user1.username).first()
    calendar = session.query(Calendar).filter_by(user_id=user.id).first()
    url = "http://127.0.0.1:5000/events/" + str(calendar.id)
    resp = client.get(url, headers=headers)
    assert resp.status_code == 200
    resp = client.get(url, headers=invalid_headers)
    assert resp.status_code == 403


def test_events_update_by_calendar(get_access_token_two_users):
    session.add(user1)
    client = app.test_client()
    token1 = get_access_token_two_users[0]['access_token']
    token2 = get_access_token_two_users[1]['access_token']
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token1
    }
    invalid_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token2
    }
    json_update_event = "{\n  \"title\" : \"new event title\" \n} "
    user = session.query(User).filter_by(username=user1.username).first()
    calendar = session.query(Calendar).filter_by(user_id=user.id).first()
    url = "http://127.0.0.1:5000/events/" + str(calendar.id)
    resp = client.post(url, headers=headers, data=json_update_event)
    assert resp.status_code == 400
    resp = client.post(url, headers=invalid_headers, data=json_update_event)
    assert resp.status_code == 403

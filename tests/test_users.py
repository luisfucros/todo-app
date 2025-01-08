import pytest
import jwt
from backend import schemas

from backend.config import settings


def test_register_user(client):
    res = client.post(
        "/users/register", json={
            "name": "hello",
            "email": "hello123@gmail.com",
            "password": "password123"
        })
    new_user = schemas.Token(**res.json())
    assert res.status_code == 201


def test_login_user(test_user, client):
    res = client.post(
        "/login", data={"username": "luis@gmail.com", "password": "password123"})
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token,
                         settings.secret_key, algorithms=[settings.algorithm])
    email = payload.get("user_email")
    assert email == "luis@gmail.com"
    assert login_res.token_type == "bearer"
    assert res.status_code == 200


@pytest.mark.parametrize("email, password, status_code", [
    ('wrongemail@gmail.com', 'password123', 403),
    ('luis@gmail.com', 'wrongpassword', 403),
    ('wrongemail@gmail.com', 'wrongpassword', 403)
])
def test_incorrect_login(test_user, client, email, password, status_code):
    res = client.post(
        "/login", data={"username": email, "password": password})

    assert res.status_code == status_code

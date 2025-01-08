from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app

from backend.config import settings
from backend.database import get_db
from backend.database import Base
from backend.oauth2 import create_access_token
from backend import models


SQLALCHEMY_DATABASE_URL = f'postgresql+psycopg2://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'


engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


def create_test_user(client, user_data):
    response = client.post("/users/register", json=user_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def test_user(client):
    user_data = {
        "id": 1,
        "name": "luis",
        "email": "luis@gmail.com",
        "password": "password123"
    }

    new_user = create_test_user(client, user_data)
    new_user.update({"id": user_data["id"], "email": user_data["email"], "password": user_data["password"]})
    return new_user


@pytest.fixture
def test_user2(client):
    user_data = {
        "id": 2,
        "name": "luis",
        "email": "luis123@gmail.com",
        "password": "password123"
    }

    new_user = create_test_user(client, user_data)
    new_user.update({"id": user_data["id"], "email": user_data["email"], "password": user_data["password"]})
    return new_user


@pytest.fixture
def token(test_user):
    return create_access_token({"user_email": test_user['email']})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client


def create_tasks(session, user_id, tasks_data):
    tasks = [models.Task(**task_data) for task_data in tasks_data]
    session.add_all(tasks)
    session.commit()
    return session.query(models.Task).filter(models.Task.owner_id == user_id).all()


@pytest.fixture
def test_tasks(test_user, session, test_user2):
    tasks_data = [{
        "title": "first task",
        "description": "first description",
        "owner_id": test_user['id']
    }, {
        "title": "second task",
        "description": "second description",
        "owner_id": test_user['id']
    },
        {
        "title": "third task",
        "description": "third description",
        "owner_id": test_user['id']
    }, {
        "title": "fourth task",
        "description": "first description",
        "owner_id": test_user['id']
    }]
    return create_tasks(session, test_user['id'], tasks_data)


@pytest.fixture
def test_tasks2(test_user2, session):
    tasks_data = [{
        "title": "first task",
        "description": "first description",
        "owner_id": test_user2['id']
    }]
    return create_tasks(session, test_user2['id'], tasks_data)

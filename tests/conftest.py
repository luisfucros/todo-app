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


@pytest.fixture
def test_user2(client):
    user_data = {
        "name": "luis",
        "email": "luis123@gmail.com",
        "password": "password123"
    }
    res = client.post("/users/register", json=user_data)

    assert res.status_code == 201

    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user


@pytest.fixture
def test_user(client):
    user_data = {
        "name": "luis",
        "email": "luis@gmail.com",
        "password": "password123"
    }
    res = client.post("/users/register", json=user_data)

    assert res.status_code == 201

    new_user = res.json()
    new_user['password'] = user_data['password']
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
        "title": "first task",
        "description": "first description",
        "owner_id": test_user2['id']
    }]

    def create_task_model(task):
        return models.Task(**task)

    task_map = map(create_task_model, tasks_data)
    tasks = list(task_map)

    session.add_all(tasks)
    session.commit()

    tasks = session.query(models.Task).all()
    return tasks

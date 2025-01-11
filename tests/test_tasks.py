import pytest
from backend import schemas


def test_get_all_tasks(authorized_client, test_tasks):
    res = authorized_client.get("/todos?limit=5&page=1")
    res_dict = res.json()

    def validate(task):
        return schemas.TaskOut(**task)
    tasks_map = map(validate, res_dict.get('data'))
    tasks_list = list(tasks_map)

    assert len(tasks_list) == len(test_tasks)
    assert res_dict.get('total') == len(tasks_list)
    assert res_dict.get('limit') == 5
    assert res_dict.get('page') == 1
    assert res.status_code == 200


def test_unauthorized_user_get_all_tasks(client, test_tasks):
    res = client.get("/todos")
    assert res.status_code == 401


@pytest.mark.parametrize("title, description", [
    ("awesome new task", "awesome new description"),
    ("walk the dog", "walking my dog in the park"),
    ("homework read", "read Crime and Punishment"),
])
def test_create_task(authorized_client, test_user, test_tasks, title, description):
    res = authorized_client.post(
        "/todos", json={"title": title, "description": description})

    created_task = schemas.TaskOut(**res.json())
    assert res.status_code == 201
    assert created_task.title == title
    assert created_task.description == description


def test_unauthorized_user_create_task(client, test_user, test_tasks):
    res = client.post(
        "/todos", json={"title": "some title", "description": "some description"})
    assert res.status_code == 401


def test_unauthorized_user_delete_task(client, test_user, test_tasks):
    res = client.delete(
        f"/todos/{test_tasks[0].id}")
    assert res.status_code == 401


def test_delete_task_success(authorized_client, test_user, test_tasks):
    res = authorized_client.delete(
        f"/todos/{test_tasks[0].id}")

    assert res.status_code == 204


def test_delete_task_non_exist(authorized_client, test_user, test_tasks):
    res = authorized_client.delete(
        f"/todos/8000000")

    assert res.status_code == 404


def test_delete_other_user_task(authorized_client, test_user, test_tasks2):
    res = authorized_client.delete(
        f"/todos/{test_tasks2[0].id}")
    assert res.status_code == 403


def test_update_task(authorized_client, test_user, test_tasks):
    data = {
        "title": "updated title",
        "description": "updatd description",
        "id": test_tasks[0].id
    }
    res = authorized_client.put(f"/todos/{test_tasks[0].id}", json=data)
    updated_task = schemas.TaskOut(**res.json())
    assert res.status_code == 200
    assert updated_task.title == data['title']
    assert updated_task.description == data['description']


def test_update_other_user_task(authorized_client, test_user, test_user2, test_tasks2):
    data = {
        "title": "updated title",
        "description": "updated content",
        "id": test_tasks2[0].id
    }
    res = authorized_client.put(f"/todos/{test_tasks2[0].id}", json=data)
    assert res.status_code == 403


def test_unauthorized_user_update_task(client, test_user, test_tasks):
    res = client.put(
        f"/todos/{test_tasks[0].id}")
    assert res.status_code == 401


def test_update_task_non_exist(authorized_client, test_user, test_tasks):
    data = {
        "title": "updated title",
        "description": "updated description",
        "id": test_tasks[3].id

    }
    res = authorized_client.put(
        f"/todos/8000000", json=data)

    assert res.status_code == 404
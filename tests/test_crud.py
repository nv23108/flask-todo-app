import pytest
import os
from app import app

@pytest.fixture
def client():
    # Clear the data file before each test
    data_file = "flask-todo-app/todo.json"
    with open(data_file, 'w') as f:
        f.write('[]')
    
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_create_task(client):
    # CREATE
    resp = client.post("/add", data={
        "task": "Buy milk",
        "description": "",
        "priority": "medium",
        "due_date": ""
    }, follow_redirects=True)
    assert resp.status_code == 200

    # READ/VERIFY
    resp2 = client.get("/search")
    assert resp2.status_code == 200
    tasks = resp2.get_json()
    assert any(t['name'] == 'Buy milk' for t in tasks)

def test_update_task(client):
    # CREATE first
    client.post("/add", data={
        "task": "Old title",
        "description": "",
        "priority": "medium",
        "due_date": ""
    }, follow_redirects=True)

    # Get task id
    resp = client.get("/search")
    tasks = resp.get_json()
    task_id = next(t['id'] for t in tasks if t['name'] == 'Old title')

    # UPDATE
    resp = client.post(f"/task/{task_id}/update", data={
        "name": "New title",
        "description": "Updated desc",
        "priority": "high",
        "due_date": ""
    })
    assert resp.status_code == 200

    # READ/VERIFY
    resp2 = client.get("/search")
    tasks = resp2.get_json()
    task = next(t for t in tasks if t['id'] == task_id)
    assert task['name'] == 'New title'
    assert task['description'] == 'Updated desc'

def test_delete_task(client):
    # CREATE first
    client.post("/add", data={
        "task": "To be deleted",
        "description": "",
        "priority": "medium",
        "due_date": ""
    }, follow_redirects=True)

    # Get task id
    resp = client.get("/search")
    tasks = resp.get_json()
    task_id = next(t['id'] for t in tasks if t['name'] == 'To be deleted')

    # DELETE
    resp = client.delete(f"/delete/{task_id}")
    assert resp.status_code == 200

    # READ/VERIFY
    resp2 = client.get("/search")
    tasks = resp2.get_json()
    assert not any(t['id'] == task_id for t in tasks)
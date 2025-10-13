import requests

base_users = "http://127.0.0.1:5000/api/users"
base_tasks = "http://127.0.0.1:5000/api/tasks"

session = requests.Session()

resp = session.post(
    f"{base_users}/login",
    json={"username": "alice", "password": "secret"},
)
print("login:", resp.status_code, resp.text)

resp = session.post(
    f"{base_tasks}/",
    json={
        "title": "Test Task",
        "description": "This is a test task.",
        "status": "0",
        "priority": "1",
    },
)
print("create:", resp.status_code, resp.text)

resp = session.get(f"{base_tasks}/")
print("get:", resp.status_code, resp.text)

tasks = resp.json() if resp.ok else []
task_id = tasks[0]["id"] if tasks else None

if task_id:
    resp = session.put(
        f"{base_tasks}/{task_id}",
        json={"title": "Updated Task"},
    )
    print("update:", resp.status_code, resp.text)

    resp = session.delete(f"{base_tasks}/{task_id}")
    print("delete:", resp.status_code, resp.text)
else:
    print("update: skipped (no task id)")
    print("delete: skipped (no task id)")

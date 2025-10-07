import requests, json

base = "http://127.0.0.1:5000/api/tasks"
user_id = 1

resp = requests.post(
    f"{base}/",
    json={
        "title": "Test Task",
        "description": "This is a test task.",
        "user_id": user_id,
    },
)
print("create:", resp.status_code, resp.text)

resp = requests.get(f"{base}/", params={"user_id": user_id})
print("get:", resp.status_code, resp.text)

tasks = resp.json() if resp.ok else []
task_id = tasks[0]["id"] if tasks else None

if task_id:
    resp = requests.put(
        f"{base}/{task_id}",
        json={"title": "Updated Task", "description": "This is an updated test task."},
    )
    print("update:", resp.status_code, resp.text)

    resp = requests.delete(f"{base}/{task_id}")
    print("delete:", resp.status_code, resp.text)
else:
    print("update: skipped (no task id)")
    print("delete: skipped (no task id)")

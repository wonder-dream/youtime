import requests, json
base = "http://127.0.0.1:5000/api/users"

resp = requests.post(
    f"{base}",
    json={"username": "alice", "email": "a@b.com", "password": "secret"}
)
print("register:", resp.status_code, resp.text)

resp = requests.post(
    f"{base}/login",
    json={"username": "alice", "password": "secret"}
)
print("login:", resp.status_code, resp.text)
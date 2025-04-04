import requests
import threading
import random

COUNT = 10_000
BASE_URL = "http://127.0.0.1:5000/"

users = [
    {"username": "admin_2", "password": "password123"},
    {"username": "not_admin", "password": "idk123"},
    {"username": "not_human", "password": "beep345"},
]

def signup(user):
    try:
        req = requests.post(f"{BASE_URL}/signup", json=user)
        print(f"[SIGNUP] {user['username']} - {req.status_code} - {req.json().get('message', '')}")
    except Exception as e:
        print(f"[SIGNUP ERROR] {user['username']}: {e}")

def simulate_actions(user):
    for i in range(COUNT):
        try:
            login_req = requests.post(f"{BASE_URL}/login", json=user)
            print(f"[LOGIN] {user['username']} - {login_req.status_code} - {login_req.text}")

            if login_req.status_code != 200:
                print(f"[LOGIN FAIL] {user['username']} ({login_req.status_code})")
                continue

            token = login_req.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}

            content = f"Paste {i} from {user['username']} - {random.randint(0,1000)}"
            paste_req = requests.post(f"{BASE_URL}/paste", json={"content": content}, headers=headers)

            if paste_req.status_code == 201:
                paste_id = paste_req.json().get("paste_id")
                print(f"[PASTE] {user['username']} - Paste ID: {paste_id}")

                # put an UPDATE every 10 iterations
                if i % 10 == 0:
                    update_res = requests.put(f"{BASE_URL}/paste/{paste_id}", json={"content": f"Updated {content}"}, headers=headers)
                    print(f"[UPDATE] {user['username']} - {update_res.status_code}")

                # put a DELETE every 15 iterations
                if i % 15 == 0:
                    del_res = requests.delete(f"{BASE_URL}/paste/{paste_id}", headers=headers)
                    print(f"[DELETE] {user['username']} - {del_res.status_code}")
            else:
                print(f"[PASTE FAIL] {user['username']} ({paste_req.status_code})")


            logout_req = requests.post(f"{BASE_URL}/logout", headers=headers)
            print(f"[LOGOUT] {user['username']} - {logout_req.status_code} - {logout_req.text}")

        except Exception as e:
            print(f"[ERROR] {user['username']} Iteration {i}: {e}")

signup_threads = [threading.Thread(target=signup, args=(user,)) for user in users]
for t in signup_threads: t.start()
for t in signup_threads: t.join()

action_threads = [threading.Thread(target=simulate_actions, args=(user,)) for user in users]
for t in action_threads: t.start()
for t in action_threads: t.join()

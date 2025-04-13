import requests
import threading
import random
import time
from collections import deque

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
    paste_history = deque(maxlen=10)

    for i in range(COUNT):
        try:
            login_req = requests.post(f"{BASE_URL}/login", json=user)
            print(f"[LOGIN] {user['username']} - {login_req.status_code} - {login_req.text}")

            if login_req.status_code != 200:
                print(f"[LOGIN FAIL] {user['username']} ({login_req.status_code})")
                continue

            token = login_req.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}

            if i % 3 == 0:
                list_res = requests.get(f"{BASE_URL}/pastes", headers=headers)
                print(f"[LIST] {user['username']} - {list_res.status_code}")

            if i % 5 == 0:
                keyword = random.choice(["beep", "paste", "update", "admin", "test", "random"])
                search_res = requests.get(f"{BASE_URL}/search", params={"keyword": keyword}, headers=headers)
                print(f"[SEARCH] {user['username']} - '{keyword}' - {search_res.status_code}")

            content = f"Paste {i} from {user['username']} - {random.randint(0,1000)}"
            paste_req = requests.post(f"{BASE_URL}/paste", json={"content": content}, headers=headers)

            if paste_req.status_code == 201:
                paste_id = paste_req.json().get("paste_id")
                paste_history.append(paste_id)  # Keep track of paste ID
                print(f"[PASTE] {user['username']} - Paste ID: {paste_id}")

                if i % 10 == 0 and paste_history:
                    pid_to_update = random.choice(list(paste_history))
                    update_res = requests.put(
                        f"{BASE_URL}/paste/{pid_to_update}",
                        json={"content": f"Updated {content}"},
                        headers=headers,
                    )
                    print(f"[UPDATE] {user['username']} - {pid_to_update} - {update_res.status_code}")

                if i % 15 == 0 and paste_history:
                    pid_to_delete = random.choice(list(paste_history))
                    del_res = requests.delete(f"{BASE_URL}/paste/{pid_to_delete}", headers=headers)
                    print(f"[DELETE] {user['username']} - {pid_to_delete} - {del_res.status_code}")
            else:
                print(f"[PASTE FAIL] {user['username']} ({paste_req.status_code})")

            logout_req = requests.post(f"{BASE_URL}/logout", headers=headers)
            print(f"[LOGOUT] {user['username']} - {logout_req.status_code} - {logout_req.text}")

            time.sleep(random.uniform(0.1, 0.3))

        except Exception as e:
            print(f"[ERROR] {user['username']} Iteration {i}: {e}")

signup_threads = [threading.Thread(target=signup, args=(user,)) for user in users]
for t in signup_threads: t.start()
for t in signup_threads: t.join()

action_threads = [threading.Thread(target=simulate_actions, args=(user,)) for user in users]
for t in action_threads: t.start()
for t in action_threads: t.join()

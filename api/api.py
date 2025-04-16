from prometheus_client import Counter, Histogram, generate_latest, REGISTRY
from flask import Flask, request, jsonify, g, Response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
import uuid
from confluent_kafka import Producer
import json
from datetime import datetime, UTC


app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "cc-proj"
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

# Kafka setup
def delivery_report(err, msg):
    if err:
        print(f"Delivery failed: {err}")
    else:
        print(f"Message delivered to topic: {msg.topic()} [{msg.partition()}]")

def send_to_kafka(topic, data):
    try:
        payload = json.dumps(data)
        producer.produce(topic, value=payload, callback=delivery_report)
        producer.flush()
    except Exception as e:
        print(f"Kafka send failed: {e}")

producer_conf = {
    "bootstrap.servers": "localhost:9092",
}
producer = Producer(producer_conf)

REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status_code"])
REQUEST_LATENCY = Histogram("http_response_time_seconds", "Request latency in seconds", ["method", "endpoint"])

@app.route("/metrics")
def metrics():
    return Response(generate_latest(REGISTRY), mimetype="text/plain")

@app.before_request
def start_timer():
    g.start_time = datetime.now(UTC)

@app.after_request
def log_request(response):
    try:
        duration = round((datetime.now(UTC) - g.start_time).total_seconds() * 1000)
        log_data = {
            "timestamp": int(datetime.now(UTC).timestamp() * 1000),
            "endpoint": request.path,
            "method": request.method,
            "status_code": response.status_code,
            "response_time_ms": duration,
            "error_message": response.json.get("error") if response.is_json and "error" in response.json else None,
            "username": get_jwt_identity() if "Authorization" in request.headers and "Bearer" in request.headers[
                "Authorization"] else "anonymous"
        }
        send_to_kafka("pastebin_api_logs", log_data)
        REQUEST_COUNT.labels(method=request.method, endpoint=request.path, status_code=response.status_code).inc()
        REQUEST_LATENCY.labels(method=request.method, endpoint=request.path).observe(duration / 1000)
    except Exception as e:
        print(f"Access log send failed: {e}")
    return response

@app.errorhandler(Exception)
def handle_exception(e):
    duration = round((datetime.now(UTC) - g.start_time).total_seconds() * 1000)
    log_data = {
        "timestamp": int(datetime.now(UTC).timestamp() * 1000),
        "endpoint": request.path,
        "method": request.method,
        "status_code": 500,
        "response_time_ms": duration,
        "error_message": str(e),
        "username": get_jwt_identity() if "Authorization" in request.headers and "Bearer" in request.headers["Authorization"] else "anonymous"
    }
    send_to_kafka("pastebin_api_logs", log_data)
    return jsonify({"error": "Internal Server Error"}), 500

# In-memory DB
users_db = {
    "admin": bcrypt.generate_password_hash("password123").decode("utf-8"),
}
pastes = {}

@app.route('/')
def root():
    return '<h1>Welcome to PasteInBin API</h1>'


@app.route("/signup", methods=["POST"])
def sign_up():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username in users_db:
        send_to_kafka("auth_topic", {
            "event": "signup",
            "username": username,
            "timestamp": int(datetime.now(UTC).timestamp() * 1000),
            "result": "failed - username already exists",
            "endpoint": "/signup",
            "method": "POST",
            "status_code": 400
        })
        return jsonify({"message": "Username already exists"}), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
    users_db[username] = hashed_pw
    send_to_kafka("auth_topic", {
        "event": "signup",
        "username": username,
        "timestamp": int(datetime.now(UTC).timestamp() * 1000),
        "result": "successfully signed up",
        "endpoint": "/signup",
        "method": "POST",
        "status_code": 201
    })
    return jsonify({"message": "User created"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    stored_password = users_db.get(username)
    if not stored_password or not bcrypt.check_password_hash(stored_password, password):
        send_to_kafka("auth_topic", {
            "event": "login",
            "username": username,
            "timestamp": int(datetime.now(UTC).timestamp() * 1000),
            "result": "failed - invalid credentials",
            "endpoint": "/login",
            "method": "POST",
            "status_code": 401
        })
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(identity=username)
    send_to_kafka("auth_topic", {
        "event": "login",
        "username": username,
        "timestamp": int(datetime.now(UTC).timestamp() * 1000),
        "result": "successfully logged in",
        "endpoint": "/login",
        "method": "POST",
        "status_code": 200
    })
    return jsonify({"message": "Logged in Successfully!", "access_token": access_token}), 200

@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    username = get_jwt_identity()
    send_to_kafka("auth_topic", {
        "event": "logout",
        "username": username,
        "timestamp": int(datetime.now(UTC).timestamp() * 1000),
        "result": "successfully logged out",
        "endpoint": "/logout",
        "method": "POST",
        "status_code": 200
    })
    return jsonify({"message": f"{username} Logged Out"}), 200



@app.route('/paste', methods=['POST'])
@jwt_required()
def create_paste():
    data = request.json
    if not data or 'content' not in data:
        return jsonify({"error": "Content is required"}), 400

    paste_id = str(uuid.uuid4())
    pastes[paste_id] = {"content": data['content'], "owner": get_jwt_identity()}

    send_to_kafka("paste_topic", {
        "event": "create_paste",
        "username": get_jwt_identity(),
        "paste_id": paste_id,
        "content": data['content'],
        "timestamp": int(datetime.now(UTC).timestamp() * 1000),
        "endpoint": "/paste",
        "method": "POST",
        "status_code": 201
    })

    return jsonify({"message": "Paste created", "paste_id": paste_id}), 201

@app.route('/paste/<paste_id>', methods=['GET'])
@jwt_required()
def get_paste(paste_id):
    paste = pastes.get(paste_id)
    if paste:
        return jsonify({"paste_id": paste_id, "content": paste["content"]}), 200
    return jsonify({"error": "Paste not found"}), 404

@app.route('/paste/<paste_id>', methods=['DELETE'])
@jwt_required()
def delete_paste(paste_id):
    username = get_jwt_identity()
    paste = pastes.get(paste_id)

    if not paste:
        return jsonify({"error": "Paste not found"}), 404

    if paste["owner"] != username:
        return jsonify({"error": "You are not authorized to delete this paste"}), 403

    del pastes[paste_id]

    send_to_kafka("paste_topic", {
        "event": "delete_paste",
        "username": username,
        "paste_id": paste_id,
        "timestamp": int(datetime.now(UTC).timestamp() * 1000),
        "endpoint": f"/paste/{paste_id}",
        "method": "DELETE",
        "status_code": 200
    })

    return jsonify({"message": "Paste deleted"}), 200


@app.route('/paste/<paste_id>', methods=['PUT'])
@jwt_required()
def update_paste(paste_id):
    username = get_jwt_identity()
    paste = pastes.get(paste_id)

    if not paste:
        send_to_kafka("paste_topic", {
            "event": "update_paste",
            "username": username,
            "paste_id": paste_id,
            "timestamp": int(datetime.now(UTC).timestamp() * 1000),
            "result": "failed - paste not found",
            "endpoint": f"/paste/{paste_id}",
            "method": "PUT",
            "status_code": 404
        })
        return jsonify({"error": "Paste not found"}), 404

    if paste["owner"] != username:
        send_to_kafka("paste_topic", {
            "event": "update_paste",
            "username": username,
            "paste_id": paste_id,
            "timestamp": int(datetime.now(UTC).timestamp() * 1000),
            "result": "failed - unauthorized",
            "endpoint": f"/paste/{paste_id}",
            "method": "PUT",
            "status_code": 403
        })
        return jsonify({"error": "You are not authorized to update this paste"}), 403

    data = request.json
    if not data or 'content' not in data:
        return jsonify({"error": "Content is required"}), 400

    paste["content"] = data['content']

    send_to_kafka("paste_topic", {
        "event": "update_paste",
        "username": username,
        "paste_id": paste_id,
        "timestamp": int(datetime.now(UTC).timestamp() * 1000),
        "result": "success",
        "endpoint": f"/paste/{paste_id}",
        "method": "PUT",
        "status_code": 200
    })

    return jsonify({"message": "Paste updated"}), 200

@app.route('/search', methods=['GET'])
@jwt_required()
def search_pastes():
    keyword = request.args.get('keyword', '').lower()
    username = get_jwt_identity()
    result = {pid: p for pid, p in pastes.items() if keyword in p["content"].lower()}

    if not result:
        send_to_kafka("access_topic", {
            "event": "search_pastes",
            "username": username,
            "keyword": keyword,
            "timestamp": int(datetime.now(UTC).timestamp() * 1000),
            "result_count": 0,
            "endpoint": "/search",
            "method": "GET",
            "status_code": 404
        })
        return jsonify({"message": "No pastes found"}), 404

    send_to_kafka("access_topic", {
        "event": "search_pastes",
        "username": username,
        "keyword": keyword,
        "timestamp": int(datetime.now(UTC).timestamp() * 1000),
        "result_count": len(result),
        "endpoint": "/search",
        "method": "GET",
        "status_code": 200
    })
    return jsonify({"results": result}), 200

@app.route('/pastes', methods=['GET'])
@jwt_required()
def list_pastes():
    username = get_jwt_identity()
    user_pastes = {pid: p for pid, p in pastes.items() if p["owner"] == username}

    if not user_pastes:
        send_to_kafka("access_topic", {
            "event": "list_pastes",
            "username": username,
            "timestamp": int(datetime.now(UTC).timestamp() * 1000),
            "result_count": 0,
            "endpoint": "/pastes",
            "method": "GET",
            "status_code": 404
        })
        return jsonify({"message": "No pastes found for this user"}), 404

    send_to_kafka("access_topic", {
        "event": "list_pastes",
        "username": username,
        "timestamp": int(datetime.now(UTC).timestamp() * 1000),
        "result_count": len(user_pastes),
        "endpoint": "/pastes",
        "method": "GET",
        "status_code": 200
    })
    return jsonify({"pastes": user_pastes}), 200

if __name__ == '__main__':
    app.run(debug=True)


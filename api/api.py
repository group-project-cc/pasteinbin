from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
import uuid

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "cc-proj"  # Secret key for JWT authentication
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

# In-memory storage 
users_db = {
    "admin": bcrypt.generate_password_hash("password123").decode("utf-8"),
}
pastes = {}  # Dictionary to store pastes

@app.route('/')
def root():
    return '<h1>Welcome to PasteBin API</h1>'

#  Signup Endpoint
@app.route("/signup", methods=["POST"])
def sign_up():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username in users_db:
        return jsonify({"message": "Username already exists"}), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
    users_db[username] = hashed_pw
    return jsonify({"message": "User created"}), 201

#  Login Endpoint
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    stored_password = users_db.get(username)
    if not stored_password or not bcrypt.check_password_hash(stored_password, password):
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(identity=username)
    return jsonify({"message": "Logged in Successfully!", "access_token": access_token}), 200

#  Logout Endpoint
@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    return jsonify({"message": f"{get_jwt_identity()} Logged Out"}), 200

#  Create a Paste (POST) 
@app.route('/paste', methods=['POST'])
@jwt_required()
def create_paste():
    data = request.json
    if not data or 'content' not in data:
        return jsonify({"error": "Content is required"}), 400
    
    paste_id = str(uuid.uuid4())  # Generate unique ID
    pastes[paste_id] = {"content": data['content'], "owner": get_jwt_identity()}
    
    return jsonify({"message": "Paste created", "paste_id": paste_id}), 201

#  Get a Paste (GET) 
@app.route('/paste/<paste_id>', methods=['GET'])
@jwt_required()
def get_paste(paste_id):
    paste = pastes.get(paste_id)
    if paste:
        return jsonify({"paste_id": paste_id, "content": paste["content"]}), 200
    return jsonify({"error": "Paste not found"}), 404

#  Delete a Paste (DELETE) 
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
    return jsonify({"message": "Paste deleted"}), 200

if __name__ == '__main__':
    app.run(debug=True)  # Run Flask in debug mode

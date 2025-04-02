from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "cc-proj"
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

users_db = {
    "admin": bcrypt.generate_password_hash("password123").decode("utf-8"),
}

"""Sign-up endpoint"""
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

"""login endpoint"""
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    stored_password = users_db.get(username)
    if not stored_password or not bcrypt.check_password_hash(stored_password, password):
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(identity=username)
    return jsonify({"message": "Logged in Successfully!!",
                    "access_token": access_token}), 200


"""logout endpoint"""
@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    return jsonify({"message": f"{get_jwt_identity()} Logged Out"}), 200

if __name__ == '__main__':
    app.run(debug=True)

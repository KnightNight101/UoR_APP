from flask import Flask, request, jsonify
from db import SessionLocal, User, init_db, register_user
from sqlalchemy import func

app = Flask(__name__)

@app.route("/api/users", methods=["GET"])
def get_users():
    init_db()
    with SessionLocal() as session:
        users = session.query(User).all()
        user_list = [
            {
                "id": user.id,
                "username": user.username,
                "created_at": user.created_at,
            }
            for user in users
        ]
    return jsonify(user_list)

@app.route("/api/user-count", methods=["GET"])
def get_user_count():
    init_db()
    with SessionLocal() as session:
        count = session.query(func.count(User.id)).scalar()
    return jsonify({"count": count})

@app.route("/api/users", methods=["POST"])
def create_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "user")
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    success = register_user(username, password, role)
    if success:
        return jsonify({"message": "User created successfully"}), 201
    else:
        return jsonify({"error": "Username already exists"}), 409

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
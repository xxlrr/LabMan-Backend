from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
import jwt
import datetime

Labman = Flask(__name__)
Labman.config["SQLALCHEMY_DATABASE_URI"] = "mysql://username:password@localhost/labman"
Labman.config["SECRET_KEY"] = "your_secret_key"
db = SQLAlchemy(Labman)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("User", "Manager"), nullable=False)
    firstname = db.Column(db.String(255))
    lastname = db.Column(db.String(255))

@Labman.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data["username"]
    password = data["password"]

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        token = jwt.encode({"user_id": user.id, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24*7)}, Labman.config["SECRET_KEY"])
        return jsonify({"role": user.role, "token": token})
    else:
        return jsonify({"message": "Invalid - Username/Password"}), 401

@Labman.route("/api/user/profile", methods=["GET"])
def get_user_profile():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"message": "Unauthorized"}), 401

    try:
        payload = jwt.decode(token, Labman.config["SECRET_KEY"], algorithms=["HS256"])
        user_id = payload["user_id"]
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token expired"}), 403
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "Bad Request"}), 400

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "firstname": user.firstname,
        "lastname": user.lastname
    })

if __name__ == "__main__":
    Labman.run(debug=True)
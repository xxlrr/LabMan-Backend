import jwt
import datetime
from flask import Blueprint, request, jsonify
from flask import current_app as Labman

from models.user import User

auth = Blueprint('auth', __name__)

@auth.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data["username"]
    password = data["password"]

    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
        token = jwt.encode({"user_id": user.id, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24*7)}, Labman.config["SECRET_KEY"])
        return jsonify({"role": user.role, "token": token})
    else:
        return jsonify({"message": "Invalid - Username/Password"}), 401
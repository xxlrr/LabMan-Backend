import jwt
from flask import Blueprint, request, jsonify
from flask import current_app as Labman

from models.user import User

user = Blueprint('user', __name__)

@user.route("/api/user/profile", methods=["GET"])
def get_user_profile():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"message": "Unauthorized"}), 401

    try:
        payload = jwt.decode(token, Labman.config["SECRET_KEY"], algorithms=["HS256"])
        user_id = payload["user_id"]
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token"}), 401

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
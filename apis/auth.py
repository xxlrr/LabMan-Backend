import jwt
import datetime
from functools import wraps
from flask import Blueprint, request, jsonify
from flask import current_app as Labman
from models.user import User

auth = Blueprint('auth', __name__)


@auth.route("/api/login/", methods=["POST"])
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
    

def get_current_user_id():
    token = request.headers.get("Authorization")
    if not token:
        return None
    payload = jwt.decode(token, Labman.config["SECRET_KEY"], algorithms=["HS256"])
    user_id = payload["user_id"]
    return user_id


def authorize(roles:list = None):
    def decorator(func):
        @wraps(func)
        def innerLayer(*args, **kwargs):
            try:
                user_id = get_current_user_id()
                user = User.query.get(user_id)
                if not user:
                    return jsonify({"message": "Unauthorized"}), 401
                if roles and user.role not in roles:
                    return jsonify({"message": "Forbidden"}), 403
            except jwt.ExpiredSignatureError:
                return jsonify({"message": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"message": "Invalid token"}), 401
            return func(*args, **kwargs)
        return innerLayer
    return decorator
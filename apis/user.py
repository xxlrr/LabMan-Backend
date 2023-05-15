from flask import Blueprint, jsonify
from apis.auth import get_current_user, authorize

user = Blueprint('user', __name__)


@user.route("/api/user/profile/", methods=["GET"])
@authorize()
def get_user_profile():
    user = get_current_user()
    return jsonify(user)
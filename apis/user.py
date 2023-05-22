from flask import Blueprint, jsonify, request
from apis.auth import get_current_user, authorize
from models.user import User
from models import db


user = Blueprint('user', __name__)


@user.route("/api/user/profile/", methods=["GET"])
@authorize()
def get_user_profile():
    user = get_current_user()
    return jsonify(user)


@user.route("/api/users/", methods=["GET"])
@authorize()
def get_Users():
    page = request.args.get("current", None, type=int)
    page_size = request.args.get("pageSize", None, type=int)
    username = request.args.get("username", "")

    query = User.query
    if username:
        query = query.filter(User.username.like(f"%{username}%"))

    paginated_users = query.paginate(page=page, per_page=page_size, error_out=False)
    total = paginated_users.total
    users = paginated_users.items

    return jsonify({
        "total": total,
        "list": users,
    }), 200

@user.route("/api/user/<int:id>/", methods=["GET"])
@authorize(["Manager"])
def get_user(id):
    user = User.query.get(id)
    return jsonify(user), 200


@user.route("/api/user/", methods=["POST"])
@authorize(["Manager"])
def add_user():
    user = User(**request.json)
    db.session.add(user)
    db.session.commit()
    return {}, 200


@user.route("/api/user/<int:id>/", methods=["PUT"])
@authorize(["Manager"])
def mod_user(id):
    User.query.filter_by(id=id).update(request.json)
    db.session.commit()
    return {}, 200


@user.route("/api/user/<int:id>/", methods=["DELETE"])
@authorize(["Manager"])
def del_user(id):
    User.query.filter_by(id=id).delete()
    db.session.commit()
    return {}, 200

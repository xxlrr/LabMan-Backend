from flask import Blueprint, jsonify, request
from apis.auth import get_current_user_id, authorize
from models.user import User
from models import db


user = Blueprint('user', __name__)


@user.route("/api/user/profile/", methods=["GET"])
@authorize()
def get_user_profile():
    """Get the current user profile."""
    user_id = get_current_user_id()
    user = User.query.get(user_id)
    return jsonify(user)


@user.route("/api/users/", methods=["GET"])
@authorize(["Manager"])
def get_Users():
    """Get the user list that meet requirements."""
    page = request.args.get("current", None, type=int)
    page_size = request.args.get("pageSize", None, type=int)
    username = request.args.get("username", "")

    query = User.query
    if username:
        query = query.filter(User.username.like(f"%{username}%"))
    query.order_by(User.id.desc())

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
    """Get a specified user."""
    user = User.query.get(id)
    return jsonify(user), 200


@user.route("/api/user/", methods=["POST"])
@authorize(["Manager"])
def add_user():
    """Add a user"""
    user = User(**request.json)
    db.session.add(user)
    db.session.commit()
    return {}, 200


@user.route("/api/user/<int:id>/", methods=["PUT"])
@authorize(["Manager"])
def mod_user(id):
    """Modify a user. You must provide all parameters."""
    User.query.filter_by(id=id).update(request.json)
    db.session.commit()
    return {}, 200


@user.route("/api/user/<int:id>/", methods=["DELETE"])
@authorize(["Manager"])
def del_user(id):
    """Delete a user"""
    User.query.filter_by(id=id).delete()
    db.session.commit()
    return {}, 200

import jwt
from flask import Flask，Blueprint, request, jsonify
from flask import current_app as Labman
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

from models.user import User

user = Blueprint('user', __name__)
auth = Blueprint('auth', __name__)


def require_role(role):
    def decorator(func):
        @wraps(func)
        def innerLayer(*args, **kwargs):
            token = request.headers.get("Authorization")
            if not token:
                return jsonify({"message": "Unauthorized"}), 401
            try:
                payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
                user_id = payload["user_id"]
                user = User.query.get(user_id)
                if not user or user.role != role:
                    return jsonify({"message": "Forbidden"}), 403
            except jwt.ExpiredSignatureError:
                return jsonify({"message": "Token expired"}), 403
            except jwt.InvalidTokenError:
                return jsonify({"message": "Invalid token"}), 403
            return func(*args, **kwargs)
        return innerLayer
    return decorator

@user.route("/api/equipment/list", methods=["GET"])
@require_role("User")
@require_role("Manager")
def get_equipment_list():
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("pageSize", 10, type=int)
    name = request.args.get("name", "")
    category = request.args.get("category", "")
    state = request.args.get("state", "")

    query = Equipment.query
    if name:
        query = query.filter(Equipment.name.like(f"%{name}%"))
    if category:
        query = query.filter(Equipment.category == category)
    if state:
        query = query.filter(Equipment.state == state)

    paginated_equipments = query.paginate(page, page_size, error_out=False)
    total = paginated_equipments.total
    equipments = paginated_equipments.items

    results = []
    for equipment in equipments:
        results.append({
            "id": equipment.id,
            "name": equipment.name,
            "category": equipment.category,
            "stock": equipment.stock,
            "description": equipment.description,
            "picture": equipment.picture,
            "state": equipment.state,
        })

    return jsonify({
        "list": results,
        "total": total,
        "current": page,
    })

@user.route("/api/equipment/<int:equipment_id>", methods=["GET"])
@require_role("User")
@require_role("Manager")
def get_equipment(equipment_id):
    equipment = Equipment.query.get(equipment_id)
    if not equipment:
        return jsonify({"message": "Invalid input"}), 400
    return jsonify({
        "id": equipment.id,
        "name": equipment.name,
        "category": equipment.category,
        "stock": equipment.stock,
        "description": equipment.description,
        "picture": equipment.picture,
        "state": equipment.state,
    })

@auth.route("/api/equipment/delete/<int:equipment_id>", methods=["DELETE"])
@require_role("Manager")
def delete_equipment(equipment_id):
    equipment = Equipment.query.get(equipment_id)
    if not equipment:
        return jsonify({"message": "Invalid input"}), 400

    db.session.delete(equipment)
    db.session.commit()

    return jsonify({"message": "OK"}), 200



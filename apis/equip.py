from flask import Blueprint, request, jsonify
from apis.auth import authorize
from models.equip import Equip
from models import db

equip = Blueprint('equip', __name__)


@equip.route("/api/equipment/", methods=["GET"])
@authorize()
def get_equips():
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("pageSize", 10, type=int)
    name = request.args.get("name", "")
    category = request.args.get("category", "")
    state = request.args.get("state", "")

    query = Equip.query
    if name:
        query = query.filter(Equip.name.like(f"%{name}%"))
    if category:
        query = query.filter(Equip.category == category)
    if state:
        query = query.filter(Equip.state == state)

    paginated_equipments = query.paginate(page=page, per_page=page_size, error_out=False)
    total = paginated_equipments.total
    equipments = paginated_equipments.items

    return jsonify({
        "total": total,
        "list": equipments,
    }), 200


@equip.route("/api/equipment/<int:id>/", methods=["GET"])
@authorize()
def get_equip(id):
    equip = Equip.query.get(id)
    return jsonify(equip), 200


@equip.route("/api/equipment/", methods=["POST"])
@authorize(["Manager"])
def add_equip():
    equip = Equip(**request.json)
    db.session.add(equip)
    db.session.commit()
    return {}, 200


@equip.route("/api/equipment/<int:id>/", methods=["PUT"])
@authorize(["Manager"])
def mod_equip(id):
    Equip.query.filter_by(id=id).update(request.json)
    db.session.commit()
    return {}, 200


@equip.route("/api/equipment/<int:id>/", methods=["DELETE"])
@authorize(["Manager"])
def del_equip(id):
    Equip.query.filter_by(id=id).delete()
    db.session.commit()
    return {}, 200

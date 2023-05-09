import jwt
from flask import Blueprint, request, jsonify
from flask import current_app as Labman

from models.user import User

user = Blueprint('user', __name__)
auth = Blueprint('auth', __name__)

@user.route("/api/equipment/search", methods=["GET"])
def searchEquipment():
    keyword = request.args.get("keyword", "")

    if keyword:
        equipments = Equipment.query.filter(Equipment.category.like(f"%{keyword}%")).all()
    else:
        equipments = Equipment.query.all()

    results = []
    for equipment in equipments:
        results.append({
            "id": equipment.id,
            "category": equipment.category,
            "stock": equipment.stock,
        })

    return jsonify(results)


@auth.route("/api/equipment/delete/<int:equipment_id>", methods=["DELETE"])
def deleteEquipment(equipment_id):
    equipment = Equipment.query.get(equipment_id)

    if not equipment:
        return jsonify({"message": "Not found"}), 404

    db.session.delete(equipment)
    db.session.commit()

    return jsonify({"message": "Successfully"}), 200



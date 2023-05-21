from flask import Blueprint, request, jsonify
from apis.auth import authorize
from models.borrow import Borrow
from models import db

borrow = Blueprint('borrow', __name__)


@borrow.route("/api/borrow/", methods=["GET"])
def get_borrows():
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("pageSize", 10, type=int)
    equip_name = request.args.get("equip_name", "")
    borrower = request.args.get("borrower", "")
    state = request.args.get("state", "")

    query = Borrow.query
    if equip_name:
        query = query.filter(Borrow.equip.name.like(f"%{equip_name}%"))
    if borrower:
        query = query.filter(Borrow.user.username == borrower)
    if state:
        query = query.filter(Borrow.state == state)

    paginated = query.paginate(page=page, per_page=page_size, error_out=False)
    total = paginated.total
    borrows = paginated.items

    return jsonify({
        "total": total,
        "list": borrows,
    }), 200


@borrow.route("/api/borrow/<int:id>/", methods=["GET"])
@authorize(["Manager"])
def get_equip(id):
    borrow = Borrow.query.get(id)
    return jsonify(borrow), 200


@borrow.route("/api/borrow/", methods=["POST"])
@authorize(["Manager"])
def add_equip():
    borrow = Borrow(**request.json)
    db.session.add(borrow)
    db.session.commit()
    return {}, 200


@borrow.route("/api/borrow/<int:id>/", methods=["PUT"])
@authorize(["Manager"])
def mod_equip(id):
    Borrow.query.filter_by(id=id).update(request.json)
    db.session.commit()
    return {}, 200


@borrow.route("/api/borrow/<int:id>/", methods=["DELETE"])
@authorize(["Manager"])
def del_equip(id):
    Borrow.query.filter_by(id=id).delete()
    db.session.commit()
    return {}, 200

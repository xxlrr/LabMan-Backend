from datetime import datetime
from flask import Blueprint, request, jsonify
from apis.auth import authorize, get_current_user_id
from models.borrow import Borrow
from models.equip import Equip
from models.user import User
from models import db

borrow = Blueprint('borrow', __name__)


@borrow.route("/api/borrow/", methods=["GET"])
@authorize()
def get_borrows():
    page = request.args.get("current", None, type=int)
    page_size = request.args.get("pageSize", None, type=int)
    equip_name = request.args.get("equip_name", "")
    borrower = request.args.get("borrower", "")
    state = request.args.get("state", "")

    user_id = get_current_user_id();
    user = User.query.get(user_id)

    query = Borrow.query
    if (user.role == "User"):
        query = query.filter(Borrow.user_id == user_id)
    if equip_name:
        query = query.filter(Equip.name.like(f"%{equip_name}%"))
    if borrower:
        query = query.filter(Borrow.user.has(username=borrower))
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
def get_borrow(id):
    borrow = Borrow.query.get(id)
    return jsonify(borrow), 200


@borrow.route("/api/borrow/", methods=["POST"])
@authorize(["Manager"])
def add_borrow():
    borrow = Borrow(**request.json)
    equip = Equip.query.get(borrow.equip_id)
    if equip.stock <= 0 or equip.state=="unavailable":
        return jsonify({"message": "the equipment is not available"}), 500 
    db.session.add(borrow)
    equip.stock -= 1
    db.session.commit()
    return {}, 200


@borrow.route("/api/borrow/<int:id>/", methods=["PUT"])
@authorize(["Manager"])
def mod_borrow(id):
    fields = request.json

    borrow_time = fields.pop('borrow_time')
    return_time = fields.pop('return_time', None)
    fields['borrow_time'] = datetime.fromisoformat(borrow_time)
    fields['return_time'] = return_time and datetime.fromisoformat(return_time)

    borrow = Borrow.query.get(id)
    if not borrow.return_time and return_time:
        borrow.equip.stock -= 1
    elif borrow.return_time and not return_time:
        borrow.equip.stock += 1

    Borrow.query.filter_by(id=borrow.id).update(fields)
    db.session.commit()
    return {}, 200


@borrow.route("/api/borrow/<int:id>/", methods=["DELETE"])
@authorize(["Manager"])
def del_borrow(id):
    Borrow.query.filter_by(id=id).delete()
    db.session.commit()
    return {}, 200


@borrow.route("/api/borrow/<int:id>/back/", methods=["PUT"])
@authorize(["Manager"])
def back_equip(id):
    borrow = Borrow.query.get(id)
    if borrow.return_time:
        return {"message": "The equipment has already been returned"}, 500
    borrow.return_time = datetime.now()
    db.session.commit()
    return {}, 200


@borrow.route("/api/borrow/reminder/count/", methods=["GET"])
@authorize()
def get_reminder_count():
  user_id = get_current_user_id()
  reminders = Borrow.query.filter_by(user_id=user_id, remind=True)
  return {"count": reminders.count()}, 200


@borrow.route("/api/borrow/reminder/", methods=["GET"])
@authorize()
def get_reminders():
    user_id = get_current_user_id()
    reminders = Borrow.query.filter_by(user_id=user_id, remind=True).all()
    return reminders, 200
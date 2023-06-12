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
    """Get the borrow list.
    If the current user is a manager (role is Manager), return all records
    If the current user is a common user (role is User), return records related to themselves.
    """
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
        query = query.join(Equip).filter(Equip.name.like(f"%{equip_name}%"))
    if borrower:
        query = query.filter(Borrow.user.has(username=borrower))
    if state:
        query = query.filter(Borrow.state == state)
    query = query.order_by(Borrow.id.desc())

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
    """Get a specified borrow record"""
    borrow = Borrow.query.get(id)
    return jsonify(borrow), 200


@borrow.route("/api/borrow/", methods=["POST"])
@authorize(["Manager"])
def add_borrow():
    """Add a borrow. If the equip stock less than 1
    or state is unavailable, return failed (code: 500).
    """
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
    """Mod a borrow record. You must specify all parameters (including unmodified)
    In this function, the equipment stock will be adjusted automatically.
    """
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
    """Delete a borrow record. If the borrowed equipment is not returned,
    the equipment stock will be +1 when the record is deleting.
    """
    borrow = Borrow.query.get(id)
    if not borrow.return_time:
        borrow.equip.stock += 1
    db.session.delete(borrow)
    db.session.commit()
    return {}, 200


@borrow.route("/api/borrow/<int:id>/back/", methods=["PUT"])
@authorize(["Manager"])
def back_equip(id):
    """Return the equipment. the return_time will be now."""
    borrow = Borrow.query.get(id)
    if borrow.return_time:
        return {"message": "The equipment has already been returned"}, 500
    borrow.return_time = datetime.utcnow()
    db.session.commit()
    return {}, 200


@borrow.route("/api/borrow/reminder/count/", methods=["GET"])
@authorize()
def get_reminder_count():
  """Get the number of reminders for the current user."""
  user_id = get_current_user_id()
  reminders = Borrow.query.filter_by(user_id=user_id, remind=True)
  return {"count": reminders.count()}, 200


@borrow.route("/api/borrow/reminder/", methods=["GET"])
@authorize()
def get_reminders():
    """Get the reminders for the current user."""
    user_id = get_current_user_id()
    reminders = Borrow.query.filter_by(user_id=user_id, remind=True).all()
    return reminders, 200
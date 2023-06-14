from datetime import datetime
from dataclasses import dataclass, field
from sqlalchemy import func, case, and_
from sqlalchemy.ext.hybrid import hybrid_property

from . import db
from .user import User
from .equip import Equip


@dataclass
class Borrow(db.Model):
    """Borrow model is used to record all borrow records."""
    state: str
    remind: bool
    id: int = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))
    equip_id = db.Column(db.Integer, db.ForeignKey('equip.id', ondelete="CASCADE"))
    borrow_time: datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    duration: int = db.Column(db.Integer, nullable=False)
    return_time: datetime = db.Column(db.DateTime, nullable=True)
    user: User = field(init=False)
    equip: Equip = field(init=False)

    @hybrid_property
    def state(self) -> str:
        """ return one of four state for this record:
        · BORROWING: retrun_time is None & current_time < borrow_time + duration
        · RETURNED: return_time is not None & return_time < borrow_time + duration
        · LATE: return_time is not None & return_time > borrow_time + duration
        · MISSING: return_time is None & current_time > borrow_time + duration
        """
        if self.return_time:
            # returned
            return "LATE" if (self.return_time - self.borrow_time).days > self.duration else "RETURNED"
        else:
            # not returned
            return "MISSING" if (datetime.utcnow() - self.borrow_time).days > self.duration else "BORROWING"

    @state.expression
    def state(cls):
        return case(
            (cls.return_time != None, case(
                (func.julianday(cls.return_time) - func.julianday(cls.borrow_time) > cls.duration, "LATE"),
                else_="RETURNED"
            )),
            else_=case(
                (func.julianday('now') - func.julianday(cls.borrow_time) > cls.duration, "MISSING"),
                else_="BORROWING"
            ),            
        )
    
    @hybrid_property
    def remind(self) -> bool:
        """ return whether the user needs to be alerted.
        return ture if return_time is None and current_time > borrow_time + duration - 3 (near-due)
        otherwise, return flase.
        Todo: The reminder date is best controlled by a variable (near-due), which is set directly to constant 3
        """
        return not self.return_time and (datetime.utcnow() - self.borrow_time).days > self.duration - 3
    
    @remind.expression
    def remind(cls):
        return and_(
            cls.return_time == None,
            func.julianday('now') - func.julianday(cls.borrow_time) > cls.duration - 3
        )

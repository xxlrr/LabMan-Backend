from datetime import datetime
from dataclasses import dataclass, field
from sqlalchemy import func, case
from sqlalchemy.ext.hybrid import hybrid_property

from . import db
from .user import User
from .equip import Equip


@dataclass
class Borrow(db.Model):
    state: str
    remind: bool
    id: int = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    equip_id = db.Column(db.Integer, db.ForeignKey('equip.id'))
    start_time: datetime = db.Column(db.DateTime, nullable=False)
    duration: int = db.Column(db.Integer, nullable=False)
    return_time: datetime = db.Column(db.DateTime, nullable=True)
    user: User = field(init=False)
    equip: Equip = field(init=False)

    @hybrid_property
    def state(self) -> str:
        """ return one of four state for this record:
        · BORROWING: retrun_time is None & current_time < start_time + duration
        · RETURNED: return_time is not None & return_time < start_time + duration
        · LATE: return_time is not None & return_time > start_time + duration
        · MISSING: return_time is None & current_time > start_time + duration
        """
        if self.return_time:
            # returned
            return "LATE" if (self.return_time - self.start_time).days > self.duration else "RETURNED"
        else:
            # not returned
            return "MISSING" if (datetime.now() - self.start_time).days > self.duration else "BORROWING"
    
    @state.expression
    def state(cls):
        return case(
            (cls.return_time != None, case(
                (func.julianday(cls.return_time) - func.julianday(cls.start_time) > cls.duration, "LATE"),
                else_="RETURNED"
            )),
            else_=case(
                (func.julianday('now') - func.julianday(cls.start_time) > cls.duration, "MISSING"),
                else_="BORROWING"
            ),            
        )
    
    @hybrid_property
    def remind(self) -> bool:
        """ return whether the user needs to be alerted.
        return ture if return_time is None and current_time > start_time + duration - 3 (near-due)
        otherwise, return flase.
        """
        return (datetime.now() - self.start_time).days > self.duration - 3
    
    @remind.expression
    def remind(cls):
        return func.julianday('now') - func.julianday(cls.start_time) > cls.duration - 3

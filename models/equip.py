from dataclasses import dataclass

from . import db

@dataclass
class Equip(db.Model):
    """Equip model is used to save all equipment"""
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(255), nullable=False)
    category: str = db.Column(db.String(255), nullable=False)
    stock: int = db.Column(db.Integer, nullable=False)
    description: str = db.Column(db.String(255))
    state: str = db.Column(db.Enum("available", "unavailable"), nullable=False, default="available")
    # todo: alter the photo column to url after implement the upload picture api
    #  (have already implemented, not commit yet)
    photo: str = db.Column(db.Text)
    borrows = db.relationship("Borrow", backref="equip", passive_deletes=True)

from dataclasses import dataclass

from . import db

@dataclass
class Equip(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(255), nullable=False)
    category: str = db.Column(db.String(255), nullable=False)
    stock: int = db.Column(db.Integer, nullable=False)
    description: str = db.Column(db.String(255))
    state: str = db.Column(db.Enum("available", "unavailable"), nullable=False, default="available")
    photo: str = db.Column(db.Text)
    
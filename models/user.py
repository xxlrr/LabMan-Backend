from dataclasses import dataclass
from . import db

@dataclass
class User(db.Model):
    """User model is used to save all user info."""
    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(255), unique=True, nullable=False)
    email: str = db.Column(db.String(255), unique=True)
    password: str = db.Column(db.String(255), nullable=False)
    role: str = db.Column(db.Enum("User", "Manager"), nullable=False)
    firstname: str = db.Column(db.String(255))
    lastname: str = db.Column(db.String(255))
    borrows = db.relationship("Borrow", backref="user", passive_deletes=True)
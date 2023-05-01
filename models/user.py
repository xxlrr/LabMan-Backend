from . import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("User", "Manager"), nullable=False)
    firstname = db.Column(db.String(255))
    lastname = db.Column(db.String(255))    

from . import db
from .user import User

def init_user_table(session):
    manage = User(id=1,
                username="a1234567",
                password="1234567",
                role="Manager",
                email="a1234567@adelaide.edu.au",
                firstname="Manager",
                lastname="M")
    user = User(id=2,
                username="a7654321", 
                password="7654321",
                role="User",
                email="a7654321@adelaide.edu.au",
                firstname="User", 
                lastname="U")
    
    session.merge(manage)
    session.merge(user)
    session.commit()

def init_db():
    db.create_all()
    init_user_table(db.session)
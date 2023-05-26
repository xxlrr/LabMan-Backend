from . import db
from .user import User

def init_user_table(session):
    """Init user table, the method should not exist, just for testing.
    You should create a sql file to init database instead of 
    running the initialization function when the server start every time.
    """
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
    """Initialize the database.
    There is a little problem, to see init_user_table comment.
    """
    db.create_all()
    init_user_table(db.session)
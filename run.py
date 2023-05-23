import os
from flask import Flask
from flask_cors import CORS
from models import db
from models.init_db import init_db
from apis.auth import auth
from apis.user import user
from apis.equip import equip
from apis.borrow import borrow

if __name__ == "__main__":
    Labman = Flask(__name__)
    Labman.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
    Labman.config["SECRET_KEY"] = "2pkay&g5&!^@rorkdigt$80a*jmad5b=ko=+75wrt_pbd5ui)l"

    # database
    db.init_app(Labman)
    with Labman.app_context():
        init_db()
    
    # register your blueprints here
    Labman.register_blueprint(auth)
    Labman.register_blueprint(user)
    Labman.register_blueprint(equip)
    Labman.register_blueprint(borrow)

    # Cross-origin resource sharing
    CORS(Labman)
    Labman.run(debug=True)

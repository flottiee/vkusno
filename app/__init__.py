# app/__init__.py
from flask import Flask
from flask_login import LoginManager
import os
from dotenv import load_dotenv

from instance.data_db import db_session

from app.models.users import User

from app.routes.auth import auth_blueprint
from app.routes.index import index_blueprint


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    login_manager = LoginManager()
    login_manager.init_app(app)

    db_session.global_init("instance/db/vkusno.db")

    @login_manager.user_loader
    def load_user(user_id):
        db_sess = db_session.create_session()
        return db_sess.get(User, user_id)

    app.register_blueprint(index_blueprint)
    app.register_blueprint(auth_blueprint)

    return app
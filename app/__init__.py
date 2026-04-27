# app/__init__.py
from flask import Flask
from flask_login import LoginManager
import os
from dotenv import load_dotenv
from instance.data_db import db_session
from app.models.users import User
from .routes.routes import setup_routes

def create_app():
    load_dotenv()
    # Указываем пути к шаблонам и статике, так как __init__ в папке app/
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')

    login_manager = LoginManager()
    login_manager.init_app(app)

    db_session.global_init("instance/db/vkusno.db")

    @login_manager.user_loader
    def load_user(user_id):
        db_sess = db_session.create_session()
        return db_sess.get(User, user_id)

    setup_routes(app)  # Настраиваем роуты
    return app
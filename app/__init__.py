# app/__init__.py
from flask import Flask, make_response, jsonify
from flask_login import LoginManager, current_user
import os
from dotenv import load_dotenv
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from sqlalchemy.orm import joinedload

from instance.data_db import db_session
from app.models.users import User
from .models.menu_item import Category, MenuItem
from .routes.routes import setup_routes

def create_app():
    load_dotenv()
    # Указываем пути к шаблонам и статике, так как __init__ в папке app/
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')
    app.config['IMAGE_FOLDER'] = os.getenv('IMAGE_FOLDER')

    csrf = CSRFProtect()
    csrf.init_app(app)
    # app.config['WTF_CSRF_ENABLED'] = False  # Отключаем CSRF для API

    login_manager = LoginManager()
    login_manager.init_app(app)

    db_session.global_init("instance/db/vkusno.db")

    @app.context_processor
    def inject_csrf():
        return {'csrf_token': generate_csrf}

    @app.context_processor
    def inject_cart_count():
        """
        Делает переменную cart_total доступной во всех шаблонах.
        Возвращает 0, если пользователь не авторизован или корзина пуста.
        """
        cart_total = 0
        cart_items_map = {}
        if current_user.is_authenticated and current_user.cart:
            dishes = current_user.cart.content.get('dishes', [])
            cart_total = len(dishes)
            cart_items_map = {item['dish_id']: item['quantity'] for item in dishes}
        return dict(cart_total=cart_total, cart_items_map=cart_items_map)

    @app.errorhandler(400)
    def csrf_error(e):
        return make_response(jsonify({'error': 'Error with CSRF token'}), 400)

    @login_manager.user_loader
    def load_user(user_id):
        db_sess = db_session.create_session()
        user = db_sess.query(User).options(joinedload(User.cart)).get(int(user_id))
        return user

    # add_data_to_db()

    setup_routes(app)  # Настраиваем роуты
    return app


def add_data_to_db():
    # Создаём сессию для работы с БД
    session = db_session.create_session()

    # Добавляем категории
    categories_data = [
        {"name": "Пицца"},
        {"name": "Салаты"},
        {"name": "Напитки"},
        {"name": "Десерты"}
    ]

    # Словарь для хранения созданных объектов категорий (по имени)
    categories = {}

    for cat_data in categories_data:
        # Проверяем, есть ли уже категория с таким именем (опционально)
        existing = session.query(Category).filter(Category.name == cat_data["name"]).first()
        if not existing:
            category = Category()
            category.name = cat_data["name"]
            session.add(category)
            categories[cat_data["name"]] = category
        else:
            categories[cat_data["name"]] = existing

    # Добавляем пункты меню
    menu_items_data = [
        {"name": "Маргарита", "description": "Томатный соус, моцарелла, базилик", "price": 450.0,
         "image_url": "images/margherita.jpg", "is_available": True, "category_name": "Пицца"},
        {"name": "Пепперони", "description": "Томатный соус, моцарелла, пепперони", "price": 520.0,
         "image_url": "images/pepperoni.jpg", "is_available": True, "category_name": "Пицца"},
        {"name": "Додо", "description": "Томатный соус, моцарелла, пепперони", "price": 520.0,
         "image_url": "images/pepperoni.jpg", "is_available": True, "category_name": "Пицца"},
        {"name": "Четыре сыра", "description": "Томатный соус, моцарелла, пепперони", "price": 520.0,
         "image_url": "images/pepperoni.jpg", "is_available": True, "category_name": "Пицца"},
        {"name": "Шашлычная", "description": "Томатный соус, моцарелла, пепперони", "price": 520.0,
         "image_url": "images/pepperoni.jpg", "is_available": True, "category_name": "Пицца"},
        {"name": "Бургерная", "description": "Томатный соус, моцарелла, пепперони", "price": 520.0,
         "image_url": "images/pepperoni.jpg", "is_available": True, "category_name": "Пицца"},
        {"name": "Цезарь", "description": "Курица, пармезан, соус Цезарь, гренки", "price": 380.0,
         "image_url": "images/caesar.jpg", "is_available": True, "category_name": "Салаты"},
        {"name": "Греческий", "description": "Огурцы, помидоры, фета, маслины", "price": 340.0,
         "image_url": "images/greek.jpg", "is_available": True, "category_name": "Салаты"},
        {"name": "Кола", "description": "Газированный напиток", "price": 120.0,
         "image_url": "images/cola.jpg", "is_available": True, "category_name": "Напитки"},
        {"name": "Тирамису", "description": "Кофейный десерт с маскарпоне", "price": 290.0,
         "image_url": "images/tiramisu.jpg", "is_available": True, "category_name": "Десерты"},
        {"name": "Котлета", "description": "Кофейный десерт с маскарпоне", "price": 290.0,
         "image_url": "images/tiramisu.jpg", "is_available": False, "category_name": "Десерты"},
    ]

    for item_data in menu_items_data:
        # Находим категорию по имени
        category = categories.get(item_data["category_name"])
        if not category:
            print(f"Категория '{item_data['category_name']}' не найдена, пропускаем {item_data['name']}")
            continue

        # Проверяем, нет ли уже такого же блюда (по имени) – опционально
        existing_item = session.query(MenuItem).filter(MenuItem.name == item_data["name"]).first()
        if existing_item:
            print(f"Блюдо '{item_data['name']}' уже существует, пропускаем")
            continue

        menu_item = MenuItem()
        menu_item.name = item_data["name"]
        menu_item.description = item_data["description"]
        menu_item.price = item_data["price"]
        menu_item.image_url = item_data["image_url"]
        menu_item.is_available = item_data["is_available"]
        menu_item.category = category  # присваиваем объект категории, SQLAlchemy сам проставит category_id

        session.add(menu_item)

    # Сохраняем все изменения в БД
    session.commit()
    print("Данные успешно добавлены в базу данных.")

# app/routes/routes.py
import os
from functools import wraps

from flask import render_template, redirect, request, url_for, abort, jsonify, session
from flask import current_app as app  # Используем current_app как замену app
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import flag_modified
from werkzeug.utils import secure_filename

from app.models.cart import Cart
from app.models.menu_item import Category, MenuItem
from instance.data_db import db_session
from app.models.users import User, RoleRequest
from app.forms.login_form import LoginForm
from app.forms.register_form import RegisterForm


# ---------- Вспомогательные функции ----------

def login_required_api(f):
    """Декоратор для API: возвращает JSON-ошибку, если пользователь не авторизован."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Вы не зарегистрированы'}), 401
        return f(*args, **kwargs)
    return decorated


def recalc_cart_price(cart, db_sess):
    """
    Пересчитывает и сохраняет актуальную стоимость корзины на основе списка блюд.
    Возвращает итоговую цену.
    """
    total = 0
    for item in cart.content.get('dishes', []):
        dish = db_sess.query(MenuItem).get(item['dish_id'])
        if dish and dish.is_available:
            total += dish.price * item['quantity']
    cart.content['price'] = total
    flag_modified(cart, 'content')
    return total

# --- AUTH ROUTES ---

def setup_routes(app):
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegisterForm()
        if form.validate_on_submit():
            if form.password.data != form.password_again.data:
                return render_template('register.html', title='Регистрация', form=form, message="Пароли не совпадают")

            db_sess = db_session.create_session()
            if db_sess.query(User).filter(User.email == form.email.data).first():
                return render_template('register.html', title='Регистрация', form=form,
                                       message="Такой пользователь уже есть")
            user = User(
                surname=form.surname.data,
                name=form.name.data,
                email=form.email.data,
                # Если почта админская, ставим роль admin сразу
                speciality="admin" if "vkusno_ochen_vkusno" in form.email.data else "customer"
            )
            user.set_password(form.password.data)
            db_sess.add(user)
            db_sess.commit()
            return redirect('/login')
        return render_template('register.html', title='Регистрация', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect("/")
            return render_template('login.html', title='Авторизация', form=form,
                                   message="Неправильный логин или пароль")
        return render_template('login.html', title='Авторизация', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect("/")

    # --- MAIN LOGIC & API ---

    @app.route('/')
    def index():
        db_sess = db_session.create_session()
        all_requests = []  # Для админа
        user_history = []  # Для пользователя

        if current_user.is_authenticated:
            if current_user.speciality == 'admin':
                # Админ видит все новые заявки
                all_requests = db_sess.query(RoleRequest).filter(RoleRequest.status == 'pending').all()
            else:
                # Пользователь видит только свои заявки (историю)
                user_history = db_sess.query(RoleRequest).filter(RoleRequest.user_id == current_user.id).order_by(
                    RoleRequest.created_at.desc()).all()

        return render_template("index.html",
                               title="Главная",
                               requests=all_requests,
                               history=user_history)

    @app.route('/apply_role', methods=['POST'])
    @login_required
    def apply_role():
        # Работа с файлом резюме (Критерий: загрузка файлов)
        file = request.files.get('resume_file')
        resume_path = ""
        if file and file.filename != '':
            filename = secure_filename(f"user_{current_user.id}_{file.filename}")
            # Убедись, что папка static/uploads/resumes создана!
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            resume_path = filename

        db_sess = db_session.create_session()
        role_req = RoleRequest(
            user_id=current_user.id,
            requested_role=request.form.get('role'),
            resume_text=request.form.get('resume_text'),
            resume_file=resume_path  # Добавь это поле в модель RoleRequest, если его нет
        )
        db_sess.add(role_req)
        db_sess.commit()
        return redirect(url_for('index'))

    # --- ADMIN ACTIONS ---

    @app.route('/admin/approve/<int:req_id>/<string:action>')
    @login_required
    def handle_request(req_id, action):
        # Явная проверка роли для безопасности и спокойствия Pylance
        if not current_user.is_authenticated or current_user.speciality != 'admin':
            abort(403)

        db_sess = db_session.create_session()
        req = db_sess.query(RoleRequest).get(req_id)

        if req:
            if action == 'accept':
                req.status = 'approved'  # type: ignore
                user = db_sess.query(User).get(req.user_id)
                if user:
                    user.speciality = str(req.requested_role)  # type: ignore
            else:
                req.status = 'rejected'  # type: ignore
            db_sess.commit()
        return redirect(url_for('index'))

    # --- MENU ---

    @app.route('/menu')
    def menu():
        db_sess = db_session.create_session()
        all_categories_with_dishes = db_sess.query(Category).options(selectinload(Category.menu_items)).all()
        return render_template("menu.html", all_categories_with_dishes=all_categories_with_dishes)

    def create_cart(db_sess, user):
        cart = Cart(content={'dishes': [], 'price': 0})
        user.cart = cart
        db_sess.add(cart)
        return cart

    @app.route('/add_to_cart', methods=['POST'])
    @login_required_api
    def add_to_cart():
        dish_id = int(request.form.get('dish_id'))  # pyright: ignore[reportArgumentType]
        db_sess = db_session.create_session()
        dish = db_sess.query(MenuItem).get(dish_id)
        if not dish or not dish.is_available: # pyright: ignore[reportGeneralTypeIssues]
            return jsonify({'error': 'Блюдо недоступно или не найдено'}), 400

        user = db_sess.merge(current_user)
        cart = user.cart
        if not cart:
            cart = Cart(content={'dishes': [], 'price': 0})
            user.cart = cart
            db_sess.add(cart)

        dishes = cart.content.setdefault('dishes', [])  # гарантирует наличие ключа
        existing = next((item for item in dishes if item['dish_id'] == dish_id), None)
        if existing:
            existing['quantity'] += 1
            new_qty = existing['quantity']
        else:
            dishes.append({'dish_id': dish_id, 'quantity': 1})
            new_qty = 1

        # Пересчёт цены после изменения
        total_price = recalc_cart_price(cart, db_sess)

        cart_items_map = {item['dish_id']: item['quantity'] for item in dishes}
        db_sess.commit()

        return jsonify({
            'cart_total': len(dishes),
            'cart_items': cart_items_map,
            'dish_quantity': new_qty
        })

    @app.route('/view_cart')
    def view_cart():
        db_sess = db_session.create_session()
        items = []  # список кортежей (название, количество)
        price = 0
        if current_user.is_authenticated:
            user = db_sess.merge(current_user)
            if user.cart:
                for entry in user.cart.content.get('dishes', []): # entry == запись из JSON массива dishes
                    dish = db_sess.query(MenuItem).get(entry['dish_id'])
                    if dish:
                        items.append((dish.name, entry['quantity'], dish.price))
                price = user.cart.content.get('price', 0)
        return render_template('cart.html',
                               names_and_quantity=items,
                               price=price)

    @app.route('/update_cart_item', methods=['POST'])
    @login_required_api
    def update_cart_item():
        dish_id = int(request.form.get('dish_id'))
        delta = int(request.form.get('delta'))  # +1 или -1
        db_sess = db_session.create_session()

        if delta not in (1, -1):
            return jsonify({'error': 'Недопустимое значение delta'}), 400

        dish = db_sess.query(MenuItem).get(dish_id)
        if not dish or not dish.is_available: # pyright: ignore[reportGeneralTypeIssues]
            return jsonify({'error': 'Блюдо недоступно или не найдено'}), 400

        user = db_sess.merge(current_user)
        cart = user.cart
        if not cart:
            return jsonify({'error': 'Корзина пуста'}), 400

        dishes = cart.content.get('dishes', [])
        item = next((i for i in dishes if i['dish_id'] == dish_id), None)
        if not item:
            return jsonify({'error': 'Блюдо не найдено в корзине'}), 404

        item['quantity'] += delta
        if item['quantity'] <= 0:
            dishes.remove(item)
            remaining_qty = 0
        else:
            remaining_qty = item['quantity']

        recalc_cart_price(cart, db_sess)
        db_sess.commit()

        return jsonify({
            'cart_total': len(dishes),
            'dish_quantity': remaining_qty
        })

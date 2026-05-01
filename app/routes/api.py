# --- API ROUTES ---
from flask import request, jsonify
from flask_login import login_user, login_required, current_user
from instance.data_db import db_session
from app.models.users import User
from flask import current_app as app


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json # Получаем данные в формате JSON
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Missing email or password"}), 400

    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == data['email']).first()

    if user and user.check_password(data['password']):
        login_user(user) # Flask-Login создаст сессию
        return jsonify({
            "status": "success",
            "user": {
                "id": user.id,
                "name": user.name,
                "role": user.speciality
            }
        }), 200
    
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

@app.route('/api/profile', methods=['GET'])
@login_required
def api_profile():
    # Возвращает данные текущего пользователя через API
    return jsonify({
        "id": current_user.id,
        "name": current_user.name,
        "surname": current_user.surname,
        "role": current_user.speciality
    })

@app.route('/api/order', methods=['POST'])
@login_required
def api_order():
    # Заглушка для будущей системы заказов
    data = request.json
    item = data.get('item')
    # Здесь в будущем будет логика записи заказа в БД
    return jsonify({
        "status": "ordered",
        "message": f"Заказ на '{item}' принят",
        "user": current_user.name
    }), 201
from flask import Blueprint, redirect, request, render_template, url_for
from flask_login import current_user
from instance.data_db import db_session
from app.models.users import RoleRequest
from flask_login import login_required


index_blueprint = Blueprint('index', __name__, template_folder='../../templates')

@index_blueprint.route('/')
def index():
    db_sess = db_session.create_session()
    
    # Если зашел админ — подгружаем все заявки для управления
    all_requests = []
    if current_user.is_authenticated and current_user.speciality == 'admin':
        all_requests = db_sess.query(RoleRequest).filter(RoleRequest.status == 'pending').all()

    return render_template("index.html", requests=all_requests)

@index_blueprint.route('/apply_role', methods=['POST'])
@login_required
def apply_role():
    db_sess = db_session.create_session()
    
    # Создаем объект заявки
    role_req = RoleRequest(
        user_id=current_user.id,
        requested_role=request.form.get('role'),
        resume_text=request.form.get('resume')
    )
    
    db_sess.add(role_req)
    db_sess.commit()
    return redirect(url_for('index.index'))
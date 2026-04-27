from flask import abort, Blueprint, redirect
from flask_login import current_user, login_required
from instance.data_db import db_session
from app.models.users import RoleRequest, User


admin_blueprint = Blueprint('admin', __name__, url_prefix='/admin')

@admin_blueprint.route('/approve_request/<int:req_id>')
@login_required
def approve_request(req_id):
    if current_user.speciality != 'admin':
        abort(403) # Запрещаем доступ не-админам

    db_sess = db_session.create_session()
    req = db_sess.query(RoleRequest).get(req_id)
    
    if req:
        req.status = 'approved'
        # Находим пользователя, подавшего заявку, и меняем ему роль
        user = db_sess.query(User).get(req.user_id)
        user.speciality = req.requested_role
        db_sess.commit()
        
    return redirect('/')
import os
from flask import render_template, redirect, request, url_for, abort
from flask import current_app as app # Используем current_app как замену app
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

from instance.data_db import db_session
from app.models.users import User, RoleRequest
from app.forms.login_form import LoginForm
from app.forms.register_form import RegisterForm


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
                return render_template('register.html', title='Регистрация', form=form, message="Такой пользователь уже есть")

            user = User(
                surname=form.surname.data,
                name=form.name.data,
                email=form.email.data,
                speciality="customer"  # Начальная роль
            )
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
            return render_template('login.html', title='Авторизация', form=form, message="Неправильный логин или пароль")
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
        all_requests = []
        # Если зашел админ или разработчик — видим список заявок
        if current_user.is_authenticated and current_user.speciality in ['admin', 'dev']:
            all_requests = db_sess.query(RoleRequest).filter(RoleRequest.status == 'pending').all()

        return render_template("index.html", title='Главная', requests=all_requests)

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
                req.status = 'approved' # type: ignore
                user = db_sess.query(User).get(req.user_id)
                if user:
                    user.speciality = str(req.requested_role) # type: ignore
            else:
                req.status = 'rejected' # type: ignore
            db_sess.commit()
        return redirect(url_for('index'))

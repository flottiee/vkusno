import sqlalchemy
from sqlalchemy import orm
from typing import cast
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from instance.data_db.db_session import SqlAlchemyBase
from datetime import datetime

# В модели User уберите поле role, если оно было статичным, 
# или оставьте его как текущую роль пользователя.

class RoleRequest(SqlAlchemyBase):
    __tablename__ = 'role_requests'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=False)
    requested_role = sqlalchemy.Column(sqlalchemy.String(20), nullable=False)  # например, 'admin' или 'manager'
    resume_text = sqlalchemy.Column(sqlalchemy.Text, nullable=False)           # мотивационное эссе
    status = sqlalchemy.Column(sqlalchemy.String(20), default='pending')      # pending, approved, rejected
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.utcnow)

    user = orm.relationship('User', backref=orm.backref('role_requests', lazy=True))


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    surname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    # Теперь при создании юзера, если роль не передана, он автоматически станет 'customer'
    speciality = sqlalchemy.Column(sqlalchemy.String, nullable=False, default='customer')
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        if self.hashed_password is None:
            return False
        return check_password_hash(cast(str, self.hashed_password), password)
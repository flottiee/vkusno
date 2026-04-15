import datetime as dt

import sqlalchemy

from instance.data_db.db_session import SqlAlchemyBase
from sqlalchemy import orm, ForeignKey


class Order(SqlAlchemyBase):
    __tablename__ = 'orders'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey('users.id'), nullable=False)     # Кто заказал
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=dt.datetime.utcnow())           # Время создания
    status = sqlalchemy.Column(sqlalchemy.String(20), default='pending')                        # Статус: pending, accepted, cooking, ready, delivered, cancelled
    total_price = sqlalchemy.Column(sqlalchemy.Float, nullable=False)                           # Итоговая сумма
    delivery_address = sqlalchemy.Column(sqlalchemy.String(200), nullable=False)                # Адрес доставки
    client_phone = sqlalchemy.Column(sqlalchemy.String(20), nullable=True)                      # Телефон клиента (дублируется на случай изменения)
    special_requests = sqlalchemy.Column(sqlalchemy.Text, nullable=True)                        # Особые пожелания
    chef_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey('users.id'), nullable=True)      # Какой повар принял заказ
    courier_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey('users.id'), nullable=True)   # Какой курьер доставляет
    status_updated_at = sqlalchemy.Column(sqlalchemy.DateTime, onupdate=dt.datetime.utcnow())   # Время последнего изменения статуса

    user = orm.relationship('User', foreign_keys=[user_id], backref='orders')
    chef = orm.relationship('User', foreign_keys=[chef_id], backref='chef_orders')
    courier = orm.relationship('User', foreign_keys=[courier_id], backref='courier_orders')
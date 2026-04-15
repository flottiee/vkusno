import datetime as dt

import sqlalchemy

from instance.data_db.db_session import SqlAlchemyBase
from sqlalchemy import orm, ForeignKey


class OrderItem(SqlAlchemyBase):
    __tablename__ = 'order_items'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    order_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey('orders.id'), nullable=False)
    menu_item_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey('menu_items.id'), nullable=False)
    quantity = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=1)            # Количество порций
    price_at_time = sqlalchemy.Column(sqlalchemy.Float, nullable=False)                    # Цена блюда на момент заказа (фиксация)

    order = orm.relationship('Order', backref='items')
    menu_item = orm.relationship('MenuItem')

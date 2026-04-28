import sqlalchemy
from sqlalchemy import orm

from instance.data_db.db_session import SqlAlchemyBase


class Cart(SqlAlchemyBase):
    __tablename__ = 'cart'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), unique=True, nullable=False)
    content = sqlalchemy.Column(sqlalchemy.JSON, nullable=False)
    user = orm.relationship('User', uselist=False, back_populates='cart')
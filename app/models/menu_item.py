import sqlalchemy

from sqlalchemy import orm

from instance.data_db.db_session import SqlAlchemyBase


class Category(SqlAlchemyBase):
    __tablename__ = 'categories'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String(50), unique=True, nullable=False)


class MenuItem(SqlAlchemyBase):
    __tablename__ = 'menu_items'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String(100), nullable=False)
    description = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    price = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    image_url = sqlalchemy.Column(sqlalchemy.String(200), nullable=True)
    is_available = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    category_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('categories.id'))
    category = orm.relationship('Category', backref='menu_items')
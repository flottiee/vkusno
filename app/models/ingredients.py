import sqlalchemy

from instance.data_db.db_session import SqlAlchemyBase


class Ingredient(SqlAlchemyBase):
    __tablename__ = 'ingredients'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String(100), unique=True, nullable=False)
    unit = sqlalchemy.Column(sqlalchemy.String(20), default='шт')
    current_quantity = sqlalchemy.Column(sqlalchemy.Float, default=0.0)
    min_quantity = sqlalchemy.Column(sqlalchemy.Float, default=0.0)
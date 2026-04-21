from flask import Blueprint, render_template
from sqlalchemy.orm import selectinload

from app.models.menu_item import MenuItem, Category
from instance.data_db import db_session

menu_blueprint = Blueprint('menu', __name__, template_folder='../../templates')

@menu_blueprint.route('/menu')
def menu():
    db_sess = db_session.create_session()
    # menu_items_list = db_sess.query(MenuItem).all()
    # for el in menu_items_list:
    #     print(el.name, el.description, el.category.name)
    all_categories_with_dishes = db_sess.query(Category).options(selectinload(Category.menu_items)).all()
    return render_template("menu.html", all_categories_with_dishes=all_categories_with_dishes)
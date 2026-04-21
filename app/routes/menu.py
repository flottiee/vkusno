from flask import Blueprint, render_template

menu_blueprint = Blueprint('menu', __name__, template_folder='../../templates')

@menu_blueprint.route('/menu')
def menu():
    # session = db_session.create_session()
    # something = session.query(Jobs).all()
    return render_template("menu.html")
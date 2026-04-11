from flask import Blueprint, render_template

index_blueprint = Blueprint('index', __name__, template_folder='../../templates')

@index_blueprint.route('/')
def index():
    # session = db_session.create_session()
    # something = session.query(Jobs).all()
    return render_template("index.html")
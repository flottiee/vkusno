from flask import Blueprint, render_template
from sqlalchemy.orm import selectinload

from instance.data_db import db_session

storage_blueprint = Blueprint('storage', __name__, template_folder='../../templates')


@storage_blueprint.route('/storage')
def storage():
    return render_template("storage.html")
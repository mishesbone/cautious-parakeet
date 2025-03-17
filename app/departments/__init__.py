from flask import Blueprint

# Create the department blueprint
departments_bp = Blueprint('departments', __name__, url_prefix='/departments', template_folder='../templates',static_folder='../static')

from app.departments import routes

#app/auth/__init__.py
from flask import Blueprint

# Create the auth blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='../templates', static_folder='../static')

# Import the routes for the auth blueprint
from . import routes

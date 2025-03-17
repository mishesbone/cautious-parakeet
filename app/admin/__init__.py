#app/admin/__init__.py
from flask import Blueprint

# Create a Blueprint for the admin module
admin_bp = Blueprint('admin', __name__, url_prefix='/admin',template_folder='../templates',static_folder='../static')

# Import admin routes here
from . import routes

# You can also perform any additional setup for the admin module here if needed


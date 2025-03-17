#app/dashboard/__init__.py
from flask import Blueprint

# Create a Blueprint for the dashboard module
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard', template_folder='../templates',static_folder='../static')

# Import the routes for the dashboard module
from app.dashboard import routes

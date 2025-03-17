from flask import Blueprint

# Create the main_bp blueprint with the required import_name parameter
main_bp = Blueprint('main', __name__, url_prefix='/main', template_folder='templates', static_folder='static')

# Import your routes here (e.g., from . import routes)

from . import routes
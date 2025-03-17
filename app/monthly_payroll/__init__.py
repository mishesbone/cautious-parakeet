from flask import Blueprint

monthly_payroll_bp = Blueprint('monthly_payroll', __name__,url_prefix='/monthly_payroll', template_folder='../templates/page', static_folder='../static')

from app.monthly_payroll import routes  # Import the routes

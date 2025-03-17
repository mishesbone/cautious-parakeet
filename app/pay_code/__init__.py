from flask import Blueprint

pay_code_bp = Blueprint('pay_code', __name__, url_prefix='/pay_code', template_folder='../templates/page', static_folder='../static')


from app.pay_code import routes
from flask import Blueprint, render_template, request, jsonify, redirect, flash


pay_slips_bp = Blueprint('pay_slips', __name__,url_prefix='/pay_slips', template_folder='../templates/page', static_folder='../static')


from app.pay_slips import routes
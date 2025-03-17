from flask import Blueprint, render_template, request, jsonify, redirect, flash


deductions_bp = Blueprint('deductions', __name__,url_prefix='/deductions', template_folder='../templates/page', static_folder='../static')


from app.deductions import routes
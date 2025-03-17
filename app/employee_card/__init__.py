from flask import Blueprint, render_template, request, jsonify, redirect, flash


employee_card_bp = Blueprint('employee_card', __name__,url_prefix='/employee_card', template_folder='../templates/page', static_folder='../static')


from app.employee_card import routes
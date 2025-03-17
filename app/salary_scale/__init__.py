from flask import Blueprint, render_template, request, jsonify, redirect, flash

salary_scale_bp = Blueprint('salary_scale', __name__,url_prefix='/salary_scale', template_folder='../templates/page', static_folder='../static')


from app.salary_scale import routes
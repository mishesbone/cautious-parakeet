#app/main/routes.py

from flask import render_template
from . import main_bp
from app.auth import auth_bp  # Import the auth blueprint

@main_bp.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@main_bp.route('/pricing', methods=['GET'])
def pricing():
    return render_template('pricing.html')

@main_bp.route('/partners', methods=['GET'])
def partners():
    return render_template('partners.html')

@main_bp.route('/contact', methods=['GET'])  
def contact():
    return render_template('contact.html')

@main_bp.route('/terms_and_conditions', methods=['GET'])
def terms_and_conditions():
    return render_template('terms_and_conditions.html', auth=auth_bp)

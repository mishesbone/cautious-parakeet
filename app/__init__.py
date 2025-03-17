import os
import random
import string
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from .config import Config
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_restful import Api
from flask_bcrypt import Bcrypt

# Initialize extensions globally
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
api = Api()
bcrypt= Bcrypt()

def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with the app instance
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.signin'  # Specifies the login view
    mail.init_app(app)
    api.init_app(app)
    
    # Initialize bcrypt correctly
    bcrypt.init_app(app)

    # Load user model for Flask-Login
    from .models import User  # Import models only after db.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Import blueprints **after** the app is created
    from app.auth import auth_bp
    from app.admin import admin_bp
    from app.dashboard import dashboard_bp
    from app.main import main_bp
    from app.departments import departments_bp
    from app.benefits import benefits_bp
    from app.deductions import deductions_bp
    from app.employee_card import employee_card_bp
    from app.pay_code import pay_code_bp
    from app.positions import positions_bp
    from app.monthly_payroll import monthly_payroll_bp
    from app.settings import settings_bp
    from app.payroll_reporting import payroll_reporting_bp
    from app.salary_scale import salary_scale_bp
    from app.pay_slips import pay_slips_bp
    from app.hr import hr_bp

    # Register blueprints
    app.register_blueprint(hr_bp, url_prefix='/hr')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(main_bp, url_prefix='/main')
    app.register_blueprint(departments_bp, url_prefix='/departments')
    app.register_blueprint(monthly_payroll_bp, url_prefix='/monthly_payroll')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    app.register_blueprint(payroll_reporting_bp, url_prefix='/payroll_reporting')
    app.register_blueprint(benefits_bp, url_prefix='/benefits')
    app.register_blueprint(deductions_bp, url_prefix='/deductions')
    app.register_blueprint(employee_card_bp, url_prefix='/employee_card')
    app.register_blueprint(positions_bp, url_prefix='/positions')
    app.register_blueprint(salary_scale_bp, url_prefix='/salary_scale')
    app.register_blueprint(pay_slips_bp, url_prefix='/payslips')
    app.register_blueprint(pay_code_bp, url_prefix='/pay_code')

    return app

#app/dashboard/routes.py
from functools import wraps
from flask import (render_template, flash, redirect, url_for, request, Blueprint,session, make_response)
from flask_login import login_required, current_user, login_user
from sqlalchemy.orm import joinedload
from app.models import Company, User, Employee, PayCode, Deduction, Benefit, Payroll, Settings,UserCompany,PaySlip,Department,Position,SalaryScale,SystemAdmin
from app.dashboard import dashboard_bp
from flask import jsonify, request
from app import db
from app.utils import user_belongs_to_company


# Inside your Flask route for dashboard
@dashboard_bp.route('/<int:company_id>/<int:user_id>', methods=['GET', 'POST'])
@login_required
@user_belongs_to_company
def dashboard(company_id, user_id):
    # Store user_id in the session securely (use a more secure session handling method)
    session['user_id'] = user_id

    # Fetch necessary data for the dashboard
    company = Company.query.get(company_id)
    users = User.query.filter_by(company_id=company_id).all()
    employees = Employee.query.filter_by(company_id=company_id).all()
    pay_codes = PayCode.query.filter_by(company_id=company_id).all()
    deductions = Deduction.query.filter_by(company_id=company_id).all()
    benefits = Benefit.query.filter_by(company_id=company_id).all()
    monthly_payroll_records = Payroll.query.filter_by(company_id=company_id).all()
    pay_slips = PaySlip.query.filter_by(company_id=company_id).all()
    
    return render_template('dashboard.html', user_id=user_id, company=company, users=users, employees=employees, company_id=company_id)


@dashboard_bp.route('/<int:company_id>/<int:user_id>/', methods=['GET', 'POST'])
@login_required
@user_belongs_to_company
def dashboard_view(company_id, user_id):

    company = Company.query.get(company_id)
    users = User.query.filter_by(company_id=company_id).all()
    employees = Employee.query.filter_by(company_id=company_id).all()
    pay_codes = PayCode.query.filter_by(company_id=company_id).all()
    deductions = Deduction.query.filter_by(company_id=company_id).all()
    benefits = Benefit.query.filter_by(company_id=company_id).all()
    monthly_payroll_records = Payroll.query.filter_by(company_id=company_id).all()
    pay_slips = PaySlip.query.filter_by(company_id=company_id).all()

    # Construct the URL for the 'dashboard' endpoint with the 'company_id'
    dashboard_url = url_for('dashboard.dashboard_view', user_id=user_id,company_id=company_id)

    template_name = 'dashboard_view.html'

    return render_template(template_name, company=company, users=users, user_id=user_id, employees=employees, company_id=company_id, dashboard_url=dashboard_url)




@dashboard_bp.route('/user/<int:user_id>')
@login_required
def user_dashboard(user_id):
    # Retrieve the user information from the database
    user = User.query.get(user_id)
    login_user(user)

    if user is None:
        return render_template('404.html'), 404

    # Query the company associated with the user
    user_company = UserCompany.query.filter_by(user_id=user.id).first()

    # Set 'company_id' based on whether the user is associated with a company
    if user_company:
        company_id = user_company.company_id
    else:
        company_id = None

    # Render the user dashboard template and pass the 'user' and 'company_id' to the template
    return render_template('user_dashboard.html', user=user, company_id=company_id)


    

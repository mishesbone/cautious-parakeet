# Import necessary modules
from flask import Blueprint, render_template, request, jsonify, redirect, flash
from app.models import PaySlip, Payroll, db
from flask_login import login_required, current_user, login_user
from app.utils import user_belongs_to_company

# Import the 'payroll_reporting' blueprint
from . import payroll_reporting_bp

@payroll_reporting_bp.route('/<int:company_id>/payroll_reporting', methods=['GET'])
@login_required
@user_belongs_to_company
def payroll_reporting(company_id):
    # Fetch payroll reporting data specific to the company
    payrolls = Payroll.query.filter_by(company_id=company_id).all()

    # Render the 'payroll_reporting_view.html' template with payroll reporting data
    template_name = 'payroll_reporting_view.html'
    return render_template(template_name, company_id=company_id, payrolls=payrolls)

@payroll_reporting_bp.route('/<int:company_id>/payroll_reporting/pay_slip/<int:pay_slip_id>', methods=['GET'])
@login_required
@user_belongs_to_company
def view_pay_slip(company_id, pay_slip_id):
    # Fetch a specific pay slip and related data
    pay_slip = PaySlip.query.get(pay_slip_id)
    if not pay_slip or pay_slip.company_id != company_id:
        flash('Pay slip not found or does not belong to the company.', 'danger')
        return redirect(url_for('payroll_reporting.payroll_reporting', company_id=company_id))

    # Render the 'view_pay_slip.html' template with the pay slip data
    template_name = 'view_pay_slip.html'
    return render_template(template_name, company_id=company_id, pay_slip=pay_slip)

# Import necessary modules
from flask import Blueprint, render_template, request, jsonify, redirect, flash
from app.models import SalaryScale,User,PayCode
from flask_login import login_required, current_user, login_user
from app.utils import user_belongs_to_company

# Import the 'salary_scale' blueprint
from app.salary_scale import salary_scale_bp
from flask import url_for


@salary_scale_bp.route('/<int:company_id>/<int:user_id>/salary_scale', methods=['GET'])
@login_required
@user_belongs_to_company
def salary_scale(company_id, user_id):
    pay_codes = PayCode.query.all() 
    user = User.query.get(user_id)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('error.html'))  # Replace 'some_error_view' with the appropriate error page

    try:
        salary_scales = SalaryScale.query.filter_by(company_id=company_id).all()
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('error.html'))  # Replace 'some_error_view' with the appropriate error page

    if not salary_scales:
        flash('No salary scales found for this company', 'info')
    salary_scale_url=url_for('salary_scale.salary_scale', company_id=company_id, user_id=user_id)
    template_name = 'page/salary_scale.html'
    return render_template(template_name, company_id=company_id, salary_scales=salary_scales,salary_scale_url=salary_scale_url,pay_codes=pay_codes)



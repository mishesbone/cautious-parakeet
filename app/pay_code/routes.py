from flask import Blueprint, render_template, request, jsonify, redirect, flash, url_for
from app.models import PayCode, db
from flask_login import login_required,current_user
from app.utils import user_belongs_to_company
from app.pay_code import pay_code_bp

@pay_code_bp.route('/<int:company_id>/<int:user_id>/pay_code', methods=['GET', 'POST'])
@login_required
@user_belongs_to_company
def paycode(company_id, user_id):
    

    # Fetch pay codes specific to the company
    pay_codes = PayCode.query.all()

    
    return render_template('page/paycode.html', company_id=company_id,user_id=current_user.id,pay_codes=pay_codes)


from flask import request, flash, redirect, url_for, render_template

@pay_code_bp.route('/<int:company_id>/<int:user_id>/pay_code/add', methods=['POST'])
@login_required
@user_belongs_to_company
def add_pay_code(company_id, user_id):
    paycodes=PayCode.query.all()
    if request.method == 'POST':
        try:
            # Extract data from form data
            paycode_name = request.form.get('name')
            payroll_type = request.form.get('payroll_type')

            # Create a new PayCode instance
            new_pay_code = PayCode(
                name=paycode_name,
                payroll_type=payroll_type,
                company_id=company_id,
            )

            # Add the new PayCode to the database
            db.session.add(new_pay_code)
            db.session.commit()

            flash("PayCode added successfully", "success")
            return redirect(url_for("dashboard.dashboard",company_id=company_id,user_id=user_id)) 

        except Exception as e:
            # Handle exceptions and provide a flash error message
            db.session.rollback()
            flash("Failed to add PayCode: " + str(e), "error")
            return redirect(url_for("dashboard.dashboard",company_id=company_id,user_id=user_id,paycodes=paycodes))  

    return "Method not allowed", 405




@pay_code_bp.route('/edit_pay_code/<int:company_id>/<int:user_id>/<int:pay_code_id>', methods=['GET', 'POST'])
@login_required
@user_belongs_to_company
def edit_pay_code(company_id, user_id, pay_code_id):
    # Fetch all paycodes
    paycodes = PayCode.query.all()

    # Fetch unique payroll types
    payroll_types = list(set(pc.payroll_type for pc in paycodes))

    # Fetch the specific PayCode by ID
    pay_code = PayCode.query.get(pay_code_id)

    if request.method == 'POST':
        # Extract data from the form
        code = request.form.get('edit_name')
        payroll_type = request.form.get('edit_payroll_type')

        if pay_code:
            # Update the PayCode attributes
            pay_code.name = code
            pay_code.payroll_type = payroll_type
            db.session.commit()  # Commit the changes to the database

        # Redirect to the dashboard or the desired page after the update
        return render_template('dashboard.html', company_id=company_id, user_id=user_id, paycodes=paycodes, payroll_types=payroll_types)

    # Render the template for editing the PayCode
    return render_template('dashboard.html', company_id=company_id, user_id=user_id, pay_code=pay_code, payroll_types=payroll_types)

@pay_code_bp.route('/delete_pay_code/<int:company_id>/<int:user_id>/<int:pay_code_id>', methods=['POST'])
@login_required
@user_belongs_to_company
def delete_pay_code(company_id, user_id, pay_code_id):
    paycodes=PayCode.query.all()
    pay_code = PayCode.query.get(pay_code_id)
    if pay_code:
        db.session.delete(pay_code)
        db.session.commit()
        flash('Pay code deleted successfully', 'success')
    else:
        flash('Pay code not found', 'error')

    return redirect(url_for('dashboard.dashboard', company_id=company_id, user_id=user_id,paycodes=paycodes))

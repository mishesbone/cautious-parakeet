# Import necessary modules
from flask import render_template, request, jsonify, redirect, flash,url_for
from app.models import Deduction, db,User,PayCode
from flask_login import login_required
from app.utils import user_belongs_to_company
# Import the 'deductions' blueprint
from app.deductions import deductions_bp


@deductions_bp.route('/deductions/<int:company_id>/<int:user_id>/deductions', methods=['GET'])
@login_required
@user_belongs_to_company
def deductions(company_id, user_id):
    # Load the user based on user_id
    user = User.query.get(user_id)

    # Fetch deductions specific to the company
    deductions = Deduction.query.filter_by(company_id=company_id).all()
    paycodes = PayCode.get_pay_codes_by_company(company_id)

    if not deductions:
        flash("No deductions found for this employee.", "info")

    # Use a constant for the template name
    template_name = 'page/deductions.html'

    # You can use url_for to generate the URL
    deductions_url = url_for('deductions.deductions', company_id=company_id, user_id=user_id)

    # Pass variables to the template using a dictionary
    context = {
        'company_id': company_id,
        'user_id': user_id,
        'deductions': deductions,
        'deductions_url': deductions_url,
        ' paycodes': paycodes,

    }
    return render_template(template_name, **context)



@deductions_bp.route('/<int:company_id>/<int:user_id>/add_deductions', methods=['POST'])
@login_required
@user_belongs_to_company
def add_deduction(company_id, user_id):
    if request.method == 'POST':
        code = request.form.get('code')
        description = request.form.get('description')
        method_of_computation = request.form.get('selectOption')

        if method_of_computation == 'Fixed Amount':  # Assuming 'FIXED AMOUNT' value
            fixed_amount = request.form.get('fixedAmount')
            percentage_of_paycode = None
        elif method_of_computation == 'Percentage of Paycode':  # Assuming 'PERCENTAGE OF PAYCODE' value
            fixed_amount = None
            percentage_of_paycode = request.form.get('percentage')
        else:
            flash('Invalid method_of_computation', 'error')
            return redirect(url_for('dashboard.dashboard', company_id=company_id, user_id=user_id))

        try:
            new_deduction = Deduction(
                company_id=company_id,
                code=code,
                description=description,
                method_of_computation=method_of_computation,
                fixed_amount=fixed_amount,
                percentage_of_paycode=percentage_of_paycode
            )

            db.session.add(new_deduction)
            db.session.commit()
            flash('Deduction added successfully', 'success')
            return redirect(url_for('dashboard.dashboard', company_id=company_id, user_id=user_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Failed to add deduction: {str(e)}', 'error')
            return redirect(url_for('deductions.deductions', company_id=company_id, user_id=user_id))

    flash('Invalid request', 'error')
    return redirect(url_for('dashboard.dashboard', company_id=company_id, user_id=user_id))




@deductions_bp.route('/<int:company_id>/<int:user_id>/delete_deduction/<int:deduction_id>', methods=['POST'])
@login_required
@user_belongs_to_company
def delete_deduction(company_id, user_id, deduction_id):
    deduction = Deduction.query.get(deduction_id)

    if deduction:
        db.session.delete(deduction)
        db.session.commit()
        flash('Deduction deleted successfully', 'success')
    else:
        flash('Deduction not found', 'danger')

    # Redirect back to the 'deductions' view after deleting a deduction
    return redirect(url_for('deductions.deductions', company_id=company_id, user_id=user_id))

@deductions_bp.route('/<int:company_id>/<int:user_id>/update_deduction/<int:deduction_id>', methods=['POST'])
@login_required
@user_belongs_to_company
def update_deduction(company_id, user_id, deduction_id):
    deduction = Deduction.query.get(deduction_id)

    if deduction:
        if request.method == 'POST':
            # Handle the POST request to update an existing deduction
            name = request.form.get('name')
            amount = request.form.get('amount')

            if not name:
                flash('Deduction name is required', 'danger')
            elif not amount:
                flash('Deduction amount is required', 'danger')
            else:
                # Update the deduction record with the new data
                deduction.name = name
                deduction.amount = amount
                db.session.commit()
                flash('Deduction updated successfully', 'success')

        # Redirect back to the 'deductions' view after updating the deduction
        return redirect(url_for('deductions.deductions', company_id=company_id, user_id=user_id))

    else:
        flash('Deduction not found', 'danger')
        return redirect(url_for('deductions.deductions', company_id=company_id, user_id=user_id))


from flask import render_template, request, jsonify, redirect, flash, url_for
from flask_login import login_required
from app import db
from app.models import PaySlip
from app.utils import user_belongs_to_company

from . import pay_slips_bp

# Route to view pay slips
@pay_slips_bp.route('/<int:company_id>/<int:user_id>', methods=['GET'])
@login_required
@user_belongs_to_company
def pay_slips(company_id, user_id):
    # Your logic to retrieve pay slips data goes here
    pay_slips = PaySlip.query.filter_by(company_id=company_id).all()

    return render_template('templates/pay_slips.html', compay_id=company_id,user_id=user_id,pay_slips=pay_slips)

# Route to add a new pay slip
@pay_slips_bp.route('/<int:company_id>/<int:user_id>/add', methods=['GET', 'POST'])
@login_required
@user_belongs_to_company
def add_pay_slip(company_id, user_id):
    if request.method == 'POST':
        # logic to add a new pay slip goes here
        # retrieve form data using request.form
        title = request.form.get('title')
        # After adding the pay slip, you can redirect to the view page or a relevant route
        flash('Pay slip added successfully', 'success')
        return redirect(url_for('pay_slips.pay_slips', company_id=company_id, user_id=user_id))

    return render_template('/pay_slips.html', company_id=company_id, user_id=user_id)

# Route to edit an existing pay slip
@pay_slips_bp.route('/<int:company_id>/<int:user_id>/edit/<int:pay_slip_id>', methods=['GET', 'POST'])
@login_required
@user_belongs_to_company
def edit_pay_slip(company_id, user_id, pay_slip_id):
    pay_slip = PaySlip.query.get(pay_slip_id)

    if request.method == 'POST':
        # logic to edit the pay slip goes here
        # retrieve form data using request.form
        title = request.form.get('title')
        # After editing the pay slip, you can redirect to the view page or a relevant route
        flash('Pay slip edited successfully', 'success')
        return redirect(url_for('pay_slips.pay_slips', company_id=company_id, user_id=user_id))

    return render_template('pay_slips.html',  company_id=company_id, user_id=user_id,pay_slip=pay_slip)

# Route to delete an existing pay slip
@pay_slips_bp.route('/<int:company_id>/<int:user_id>/delete/<int:pay_slip_id>', methods=['POST'])
@login_required
@user_belongs_to_company
def delete_pay_slip(company_id, user_id, pay_slip_id):
    pay_slip = PaySlip.query.get(pay_slip_id)

    # Your logic to delete the pay slip goes here
    # You can use the db.session to delete the pay slip and commit the changes
    db.session.delete(pay_slip)  # Delete the pay slip
    db.session.commit()  # Commit the changes to the database

    # After deleting the pay slip, you can redirect to the view page or a relevant route
    flash('Pay slip deleted successfully', 'success')

    return redirect(url_for('pay_slips.pay_slips', company_id=company_id, user_id=user_id))

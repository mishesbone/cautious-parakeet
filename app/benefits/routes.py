from flask import Blueprint, render_template, request, jsonify, redirect, flash, url_for
from app.models import Benefit 
from app import db
from app.benefits import benefits_bp
from flask_login import login_required
from app.utils import user_belongs_to_company


# Import your models and any other necessary dependencies here
from app.models import Benefit  # Replace 'Benefit' with your actual model

# Define routes for the 'benefits' module
@benefits_bp.route('/<int:company_id>/<int:user_id>/benefits', methods=['GET'])
@login_required
@user_belongs_to_company
def benefits(company_id, user_id):
    # Fetch benefits specific to the company
    benefits = Benefit.get_benefits_by_company(company_id)

    # Render the 'benefits_view.html' template with a list of benefits
    template_name = 'benefits.html'
    return render_template(template_name, company_id=company_id, user_id=user_id, benefits=benefits)


@benefits_bp.route('/<int:company_id>/<int:user_id>/add_benefits', methods=['POST'])
@login_required
@user_belongs_to_company
def add_benefit(company_id, user_id):
    if request.method == 'POST':
        # Get data from the request
        code = request.form.get('benefitCode')
        description = request.form.get('benefitDescription')
        method_of_computation = request.form.get('selectOption')

        # Handling different methods of computation
        if method_of_computation == 'Fixed Amount':  # Fixing whitespace
            fixed_amount = request.form.get('fixedAmount')
            percentage_of_paycode = None
        elif method_of_computation == 'Percentage of Paycode':  # Fixing whitespace
            fixed_amount = None
            percentage_of_paycode = request.form.get('percentage')
        else:
            flash('Invalid method of computation', 'error')
            return redirect(url_for('dashboard.dashboard', company_id=company_id, user_id=user_id))

        # Creating a new benefit object
        new_benefit = Benefit(
            company_id=company_id,
            code=code,
            description=description,
            method_of_computation=method_of_computation,
            fixed_amount=fixed_amount,
            percentage_of_paycode=percentage_of_paycode
            # Add any additional fields from the form as needed
        )

        # Add the new benefit to the database
        db.session.add(new_benefit)
        db.session.commit()

        # Flash a success message
        flash('Benefit added successfully', 'success')

        # Redirect back to the 'benefits' view after adding a benefit
        return redirect(url_for('benefits.benefits', company_id=company_id, user_id=user_id))

    flash('Invalid request', 'error')
    return redirect(url_for('dashboard.dashboard', company_id=company_id, user_id=user_id))


# Delete a benefit
@benefits_bp.route('/<int:company_id>/<int:user_id>/delete_benefit/<int:benefit_id>', methods=['POST'])
@login_required
@user_belongs_to_company
def delete_benefit(benefit_id):
    # Fetch the benefit entry to be deleted
    benefit = Benefit.query.get(benefit_id)

    if benefit:
        # Perform the deletion
        db.session.delete(benefit)
        db.session.commit()
        flash('Benefit deleted successfully', 'success')
    else:
        flash('Benefit not found', 'danger')

    return redirect(url_for('dashboard.dashboard', company_id=company_id, user_id=user_id))

# Edit a benefit
@benefits_bp.route('/<int:company_id>/<int:user_id>/update_benefit/<int:benefit_id>', methods=['GET', 'POST'])
@login_required
@user_belongs_to_company
def update_benefit(benefit_id):
    # Fetch the benefit entry to be edited
    benefit = Benefit.query.get(benefit_id)

    if not benefit:
        flash('Benefit not found', 'danger')
        return redirect(url_for('benefits.benefits', company_id=company_id, user_id=user_id))

    if request.method == 'POST':
        # Handle the form submission for editing
        new_benefit_data = request.form  # Assuming you have a form to submit the edited data
        benefit.name = new_benefit_data['name']
        benefit.description = new_benefit_data['description']

        db.session.commit()
        flash('Benefit edited successfully', 'success')
        return redirect(url_for('benefits.benefits', company_id=company_id, user_id=user_id))
    
    return render_template('dashboard.html', benefit=benefit)

# Import necessary modules
from flask import Blueprint, render_template, request, jsonify, redirect, flash, url_for
from app.models import Position,User,Employee
from app import db
from flask_login import login_required, current_user, login_user
from app.utils import user_belongs_to_company
# Import the 'positions' blueprint
from app.positions import positions_bp

@positions_bp.route('/<int:company_id>/<int:user_id>/positions', methods=['GET'])
@login_required
@user_belongs_to_company
def positions(company_id, user_id):
    # Load the user based on user_id (assuming it's required elsewhere)
    user = User.query.get(user_id)

    # Fetch position data specific to the company
    positions = Position.query.all()
    employees=Employee.query.all()


    # Use a dictionary to pass variables to the template
    context = {
        'company_id': company_id,
        'positions': positions,
        'user_id': current_user.id,
        'employees':employees,
    }

    # Render the 'positions_view.html' template with position data
    return render_template('page/positions.html', **context)


@positions_bp.route('/<int:company_id>/<int:user_id>/positions/add', methods=['POST'])
@login_required
@user_belongs_to_company
def add_position(company_id,user_id):


    if request.method == 'POST':
        # Get the position name from the form data
        new_position = request.form.get('new_position')
        description=request.form.get('description')
        employee_id=request.form.get('employee_id')

        # Check if the new position name is provided
        if new_position:
            # Create a new Position instance and add it to the database
            new_position = Position(name=new_position, description=description)
            db.session.add(new_position)
            db.session.commit()
            flash('New position added successfully', 'success')
        else:
            flash('Position name is required', 'error')

    # Redirect back to the positions page
    return redirect(url_for('dashboard.dashboard', company_id=company_id,user_id=current_user.id,new_position=new_position))


@positions_bp.route('/<int:company_id>/positions/delete/<int:position_id>', methods=['POST'])
@login_required
@user_belongs_to_company
def delete_position(company_id, position_id):
    # Fetch user_id, assuming you're using Flask-Login
    user_id = current_user.id

    if request.method == 'POST':
        # Find the position to delete
        position_to_delete = Position.query.get(position_id)

        if position_to_delete:
            
            
                # Remove the position from the database
            db.session.delete(position_to_delete)
            db.session.commit()
            flash('Position deleted successfully', 'success')
            
        else:
            flash('Position not found', 'error')

    return redirect(url_for('dashboard.dashboard', company_id=company_id, user_id=user_id))


@positions_bp.route('/<int:company_id>/positions/edit/<int:position_id>', methods=['POST'])
@login_required
@user_belongs_to_company
def edit_position(company_id, position_id):
    # Fetch user_id, assuming you're using Flask-Login
    user_id = current_user.id
    positions = Position.query.all()

    if request.method == 'POST':
        # Find the position to edit
        position_to_edit = Position.query.get(position_id)

        if position_to_edit:
            
                # Modify the position details
            new_name = request.form.get('edited_name')
            new_description = request.form.get('edited_description')
                
                # Update the position details
            position_to_edit.name = new_name
            position_to_edit.description = new_description
                
            db.session.commit()
            flash('Position edited successfully', 'success')
        else:
                flash('Position does not Exist', 'error')
        
    return redirect(url_for('dashboard.dashboard', company_id=company_id, user_id=user_id,positions=positions))

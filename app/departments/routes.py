from flask import Blueprint, render_template, request, jsonify, redirect, flash
from app.models import Department,User
from app.departments import departments_bp
from flask_login import login_required,current_user
from app.utils import user_belongs_to_company
from flask_login import UserMixin
from app import db
from flask import request, jsonify, redirect, url_for


@departments_bp.route('/departments/<int:company_id>/<int:user_id>', methods=['GET', 'POST'])
@login_required
@user_belongs_to_company
def departments(company_id, user_id):
    # Fetch departments for the company
    departments = Department.query.all()

    # Ensure that the user fetched from the database is the same as the current_user
     # Load the user based on user_id
    user = User.query.get(user_id) 
    if user != current_user:
        # Handle the case where the user fetched is not the same as the current_user
        # return an error or redirect as needed.
        # For simplicity, we'll return an error message.
        return "Unauthorized access."

    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            department = Department(name=name)
            db.session.add(department)
            db.session.commit()
            return redirect(url_for('dashboard.dashboard', company_id=company_id, user_id=user_id))

    # Render the 'departments_view.html' template with the list of departments
    template_name = 'page/departments.html'
    return render_template(template_name, company_id=company_id, user_id=user_id, user=user, departments=departments)

@departments_bp.route('/delete_department/<int:company_id>/<int:user_id>/<int:department_id>', methods=['POST'])
def delete_department(company_id, user_id, department_id):
    print(f"Company ID: {company_id}, User ID: {user_id}, Department ID: {department_id}")
    
    # Retrieve the department from the database
    department = Department.query.get(department_id)
    print(department)  # Check the department found
    
    if department:
        # Delete the department
        db.session.delete(department)
        db.session.commit()
        
        # Redirect back to the departments_view after deletion
        return redirect(url_for('dashboard.dashboard', company_id=company_id, user_id=user_id))

    # If the department does not exist, you can handle this case accordingly (e.g., show an error message).
    flash('Department not found.', 'error')
    return redirect(url_for('dashboard.dashboard', company_id=company_id, user_id=user_id))

@departments_bp.route('/add_department/<int:company_id>/<int:user_id>', methods=['POST'])
def add_department(company_id, user_id):
    if request.method == 'POST':
        # Retrieve the department name from the form data
        name = request.form.get('name')


       
        # Create a new department instance and add it to the database
        department = Department(name=name)
        db.session.add(department)
        db.session.commit()

        # Redirect back to the departments_view after adding the department
        return redirect(url_for('dashboard.dashboard', company_id=company_id, user_id=user_id))

    # If the form submission is invalid or the department name is missing, handle it accordingly.
    flash('Invalid department name.', 'error')
    return redirect(url_for('dashboard.dashboard', company_id=company_id, user_id=user_id))

@departments_bp.route('/edit_department/<int:company_id>/<int:department_id>', methods=['GET','POST'])
@login_required
def edit_department(company_id, department_id):
    # Retrieve the department instance from the database
    department = Department.query.get(department_id)

    if not department:
        flash('Department not found.', 'error')
        return redirect(url_for('dashboard.dashboard', company_id=company_id, user_id=current_user.id))

    if request.method == 'POST':
        # Get the updated values from the form
        edited_name = request.form.get('edited_name')
        edited_description = request.form.get('edited_description')

        # Update the department attributes
        department.name = edited_name
        department.description = edited_description

        # Commit changes to the database
        db.session.commit()

        return redirect(url_for('dashboard.dashboard', company_id=company_id, user_id=current_user.id))

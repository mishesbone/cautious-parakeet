from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from . import admin_bp
from ..models import Department, User, db, SystemAdmin, Role,roles_users,Company
from ..forms import AdminForm,RoleAssignmentForm,RoleEditForm,CompanySelectionForm
from functools import wraps
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired
from wtforms.fields import SelectMultipleField
from wtforms.validators import DataRequired
from flask import render_template, request, redirect, flash


# Define a custom decorator to check if the current user has admin permissions
def admin_required(func):
    @wraps(func)  # This ensures that the decorated function keeps its name and docstring
    def decorated_view(*args, **kwargs):
        if current_user.is_authenticated and (current_user.has_permission('admin') or current_user.is_admin):
            return func(*args, **kwargs)
        else:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('dashboard.dashboard', company_id=current_user.company_id))
    return decorated_view


@admin_bp.route('/users', endpoint='admin_users')
@login_required
@admin_required
def admin_users():
    # Admin user management logic goes here
    users = User.query.all()
    return render_template('users.html', users=users)
# Route for the admin dashboard
@admin_bp.route('/<int:user_id>', methods=['GET', 'POST'], endpoint='admin_dashboard')
@login_required
@admin_required
def admin_dashboard(user_id):
    company_selection_form = CompanySelectionForm() 
    company_id = current_user.company_id
    if company_selection_form.validate_on_submit():
        selected_company_id = company_selection_form.company.data

    
    # Query to retrieve user names and role names
    user_role_query = db.session.query(
        User.name.label('user_name'),
        Role.name.label('role_name'),
        User.id.label('user_id'),  
        Role.id.label('role_id')  
    ).join(
        roles_users,
        User.id == roles_users.c.user_id
    ).join(
        Role,
        Role.id == roles_users.c.role_id
    )

    # Execute the query and fetch the results
    user_role_assignments = user_role_query.all()

    # Check if the current user is an admin
    is_admin = current_user.is_admin

    # Initialize the RoleAssignmentForm with user and role choices
    role_assignment_form = RoleAssignmentForm(
        user_choices=[(user.id, user.name) for user in User.query.all()],
        role_choices=[(role.id, role.name) for role in Role.query.all()]
    )

    role_edit_form = RoleEditForm()  # Initialize the RoleEditForm

    if is_admin:
        # Handle role assignment to other users
        if request.method == 'POST':
            # Process the form data and assign roles to other users
            if role_assignment_form.validate_on_submit():
                # Get the selected user and roles from the form data
                selected_user_id = role_assignment_form.user.data
                selected_roles = role_assignment_form.roles.data

                # Fetch the user and roles from the database
                user = User.query.get(selected_user_id)
                roles = Role.query.filter(Role.id.in_(selected_roles)).all()

                # Assign the selected roles to the user
                user.roles = roles  # Adjust the attribute based on your User model
                db.session.commit()
                flash('Roles assigned to the user successfully.', 'success')

        # Handle role editing, role deleting, and role assigning
        if role_edit_form.validate_on_submit():
            selected_user_id = user_id  # The user to edit roles for
            selected_role_id = role_edit_form.role.data
            action = role_edit_form.action.data

            # Fetch the user and role from the database
            user = User.query.get(selected_user_id)
            role = Role.query.get(selected_role_id)

            if action == 'edit':
                # Edit the role (modify role attributes here)
                # role.name = updated_name
                db.session.commit()
                flash('Role updated successfully.', 'success')

            elif action == 'delete':
                # Remove the role from the user
                user.roles.remove(role)
                db.session.commit()
                flash('Role deleted from the user.', 'success')

            elif action == 'assign':
                # Assign the role to the user
                user.roles.append(role)
                db.session.commit()
                flash('Role assigned to the user.', 'success')

    return render_template('admin_dashboard.html',company_selection_form=company_selection_form, is_admin=is_admin, role_assignment_form=role_assignment_form, role_edit_form=role_edit_form, user_role_assignments=user_role_assignments,company_id=company_id)

# Route for editing roles
@admin_bp.route('/edit_role/<string:user_name>/<string:role_name>', methods=['GET', 'POST'], endpoint='edit_role')
@login_required
@admin_required
def edit_role(user_name, role_name):

    # Query the user and role objects based on their names
    user = User.query.filter_by(name=user_name).first()
    role = Role.query.filter_by(name=role_name).first()

    if not user or not role:
        # Handle cases where user or role with the given name does not exist
        flash('User or Role not found', 'error')
        return redirect(url_for('admin.admin_dashboard'))  # Redirect to the admin dashboard or another appropriate page

    # Create a form to edit the role
    form = RoleEditForm()

    if form.validate_on_submit():
        # Process the form data for role editing
        new_role_name = form.role_name.data  # Replace with the actual form field name
        # Update the role attributes with new data
        role.name = new_role_name  # Modify role attributes as needed
        db.session.commit()
        flash('Role updated successfully.', 'success')

    return render_template('edit_role.html', user=user, role=role, form=form)

# Route for deleting roles
@admin_bp.route('/delete_role/<int:user_id>/<int:role_id>', methods=['POST'], endpoint='delete_role')
@login_required
@admin_required
def delete_role(user_id, role_id):
    # Get the user and role
    user = User.query.get(user_id)
    role = Role.query.get(role_id)

    if user and role:
        user.roles.remove(role)
        db.session.commit()
        flash(f"Role '{role.name}' deleted from user '{user.name}'", 'success')
    else:
        flash("Role or user not found", 'danger')

    return redirect(url_for('admin.admin_dashboard', user_id=user_id))
    
# Route for assigning roles
@admin_bp.route('/assign_role/<int:user_id>', methods=['POST'], endpoint='assign_role')
@login_required
@admin_required
def assign_role(user_id):
    # Get the user from the user_id provided in the URL
    user = User.query.get(user_id)

    if user:
        role_id = request.form.get('role_id')  # Retrieve the selected role ID from the form
        role = Role.query.get(role_id)

        if role:
            user.roles.append(role)
            db.session.commit()
            flash(f"Role '{role.name}' assigned to user '{user.name}'", 'success')
        else:
            flash("Role not found", 'danger')
    else:
        flash("User not found", 'danger')

    return redirect(url_for('admin.admin_dashboard', user_id=user_id))


# Route for creating a new admin user
@admin_bp.route('/create_admin', methods=['GET', 'POST'], endpoint='create_admin')
@login_required
@admin_required
def create_admin():
    form = AdminForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        is_admin = form.is_admin.data

        # Create a new admin user
        new_user = User(username=username, email=email, is_admin=is_admin)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('Admin user created successfully.', 'success')
        return redirect(url_for('admin.admin_dashboard', user_id=new_user.id))

    return render_template('create_admin.html', form=form)  

# Route for deleting a user
@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'], endpoint='delete_user')
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)

    if user:
        db.session.delete(user)
        db.session.commit()
        flash(f"User '{user.name}' deleted successfully.", 'success')
    else:
        flash("User not found", 'danger')

    return redirect(url_for('admin.admin_dashboard'))

# Route for creating a new role for a user
@admin_bp.route('/create_role', methods=['POST'], endpoint='create_role')
@login_required
@admin_required
def create_role():
    role_name = request.form.get('role_name')

    if role_name:
        new_role = Role(name=role_name)
        db.session.add(new_role)
        db.session.commit()
        flash(f"Role '{role_name}' created successfully.", 'success')
    else:
        flash("Role name is required", 'danger')

    return redirect(url_for('admin.admin_dashboard'))

# Route for deleting a role
@admin_bp.route('/delete_role/<int:role_id>', methods=['POST'], endpoint='delete_role_only')
@login_required
@admin_required
def delete_role_only(role_id):
    role = Role.query.get(role_id)

    if role:
        # Check if role is assigned to any users
        if role.users.count() > 0:
            flash("Cannot delete role that is assigned to users", 'danger')
        else:
            db.session.delete(role)
            db.session.commit()
            flash(f"Role '{role.name}' deleted successfully.", 'success')
    else:
        flash("Role not found", 'danger')

    return redirect(url_for('admin.admin_dashboard'))

# Route for editing a role  
@admin_bp.route('/edit_role/<int:role_id>', methods=['POST'], endpoint='edit_role_only')
@login_required
@admin_required 
def edit_role_only(role_id):
    role = Role.query.get(role_id)
    new_role_name = request.form.get('role_name')

    if role and new_role_name:
        role.name = new_role_name
        db.session.commit()
        flash(f"Role '{new_role_name}' updated successfully.", 'success')
    else:
        flash("Role not found or new role name is empty", 'danger')

    return redirect(url_for('admin.admin_dashboard'))

# Route for assigning a role to a user  
@admin_bp.route('/assign_role', methods=['POST'], endpoint='assign_role_only')
@login_required
@admin_required
def assign_role_only():
    user_id = request.form.get('user_id')
    role_id = request.form.get('role_id')

    user = User.query.get(user_id)
    role = Role.query.get(role_id)

    if user and role:
        user.roles.append(role)
        db.session.commit()
        flash(f"Role '{role.name}' assigned to user '{user.name}'", 'success')
    else:
        flash("User or role not found", 'danger')

    return redirect(url_for('admin.admin_dashboard'))

# Route for unassigning a role from a user
@admin_bp.route('/unassign_role', methods=['POST'], endpoint='unassign_role')
@login_required
@admin_required
def unassign_role():
    user_id = request.form.get('user_id')
    role_id = request.form.get('role_id')

    user = User.query.get(user_id)
    role = Role.query.get(role_id)

    if user and role:
        user.roles.remove(role)
        db.session.commit()
        flash(f"Role '{role.name}' unassigned from user '{user.name}'", 'success')
    else:
        flash("User or role not found", 'danger')

    return redirect(url_for('admin.admin_dashboard'))

# Route for creating a new company
@admin_bp.route('/create_company', methods=['POST'], endpoint='create_company')
@login_required
@admin_required
def create_company():
    company_name = request.form.get('company_name')

    if company_name:
        new_company = Company(name=company_name)
        db.session.add(new_company)
        db.session.commit()
        flash(f"Company '{company_name}' created successfully.", 'success')
    else:
        flash("Company name is required", 'danger')

    return redirect(url_for('admin.admin_dashboard'))



# Route for deleting a company
@admin_bp.route('/delete_company/<int:company_id>', methods=['POST'], endpoint='delete_company')
@login_required
@admin_required
def delete_company(company_id):
    company = Company.query.get(company_id)

    if company:
        db.session.delete(company)
        db.session.commit()
        flash(f"Company '{company.name}' deleted successfully.", 'success')
    else:
        flash("Company not found", 'danger')

    return redirect(url_for('admin.admin_dashboard'))

# Route for editing a company
@admin_bp.route('/edit_company/<int:company_id>', methods=['POST'], endpoint='edit_company')
@login_required
@admin_required
def edit_company(company_id):
    company = Company.query.get(company_id)
    new_name = request.form.get('company_name')

    if company and new_name:
        company.name = new_name
        db.session.commit()
        flash(f"Company name updated successfully.", 'success')
    else:
        flash("Company not found or new company name is empty", 'danger')

    return redirect(url_for('admin.admin_dashboard'))

# Route for assigning a company to a user
@admin_bp.route('/assign_company', methods=['POST'], endpoint='assign_company')
@login_required
@admin_required
def assign_company():
    user_id = request.form.get('user_id')
    company_id = request.form.get('company_id')

    user = User.query.get(user_id)
    company = Company.query.get(company_id)

    if user and company:
        user.company = company
        db.session.commit()
        flash(f"Company '{company.name}' assigned to user '{user.name}'", 'success')
    else:
        flash("User or company not found", 'danger')

    return redirect(url_for('admin.admin_dashboard'))

# Route for unassigning a company from a user
@admin_bp.route('/unassign_company', methods=['POST'], endpoint='unassign_company')
@login_required
@admin_required
def unassign_company():
    user_id = request.form.get('user_id')
    company_id = request.form.get('company_id')

    user = User.query.get(user_id)
    company = Company.query.get(company_id)

    if user and company:
        user.company = None
        db.session.commit()
        flash(f"Company '{company.name}' unassigned from user '{user.name}'", 'success')
    else:
        flash("User or company not found", 'danger')

    return redirect(url_for('admin.admin_dashboard'))

# Route for creating a new department
@admin_bp.route('/create_department', methods=['POST'], endpoint='create_department')
@login_required
@admin_required
def create_department():
    department_name = request.form.get('department_name')

    if department_name:
        new_department = Department(name=department_name)
        db.session.add(new_department)
        db.session.commit()
        flash(f"Department '{department_name}' created successfully.", 'success')
    else:
        flash("Department name is required", 'danger')

    return redirect(url_for('admin.admin_dashboard'))

# Route for deleting a department
@admin_bp.route('/delete_department/<int:department_id>', methods=['POST'], endpoint='delete_department')
@login_required
@admin_required
def delete_department(department_id):
    department = Department.query.get(department_id)

    if department:
        db.session.delete(department)
        db.session.commit()
        flash(f"Department '{department.name}' deleted successfully.", 'success')
    else:
        flash("Department not found", 'danger')

    return redirect(url_for('admin.admin_dashboard'))

# Route for editing a department
@admin_bp.route('/edit_department/<int:department_id>', methods=['POST'], endpoint='edit_department')
@login_required
@admin_required
def edit_department(department_id):
    department = Department.query.get(department_id)
    new_name = request.form.get('department_name')

    if department and new_name:
        department.name = new_name
        db.session.commit()
        flash(f"Department name updated successfully.", 'success')
    else:
        flash("Department not found or new department name is empty", 'danger')

    return redirect(url_for('admin.admin_dashboard'))


# Route for assigning a department to a user
@admin_bp.route('/assign_department', methods=['POST'], endpoint='assign_department')
@login_required
@admin_required
def assign_department():
    user_id = request.form.get('user_id')
    department_id = request.form.get('department_id')

    user = User.query.get(user_id)
    department = Department.query.get(department_id)

    if user and department:
        user.department = department
        db.session.commit()
        flash(f"Department '{department.name}' assigned to user '{user.name}'", 'success')
    else:
        flash("User or department not found", 'danger')

    return redirect(url_for('admin.admin_dashboard'))

# Route for unassigning a department from a user
@admin_bp.route('/unassign_department', methods=['POST'], endpoint='unassign_department')
@login_required
@admin_required
def unassign_department():
    user_id = request.form.get('user_id')
    department_id = request.form.get('department_id')

    user = User.query.get(user_id)
    department = Department.query.get(department_id)

    if user and department:
        user.department = None
        db.session.commit()
        flash(f"Department '{department.name}' unassigned from user '{user.name}'", 'success')
    else:
        flash("User or department not found", 'danger')

    return redirect(url_for('admin.admin_dashboard'))



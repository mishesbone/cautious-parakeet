# Import necessary modules
from functools import wraps
from flask import flash, redirect, url_for, request
from app.models import User, Company
from flask_login import current_user

# Custom decorator to check if the user belongs to the specified company
def user_belongs_to_company(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.company_id == kwargs.get('company_id'):
            return func(*args, **kwargs)
        else:
            flash("You don't have access to this company's data.", 'danger')
            user_id = kwargs.get('user_id')
            return redirect(url_for('auth.index', user_id=current_user.id))
    return decorated_function

# Custom decorator to check if the user is an admin
def user_is_admin(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.is_admin:
            return func(*args, **kwargs)
        else:
            flash("You don't have access to this page.", 'danger')
            return redirect(url_for('auth.index', user_id=current_user.id))
    return decorated_function

# Custom decorator to check if the user is an HR manager
def user_is_hr_manager(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.role == 'HR_MANAGER':
            return func(*args, **kwargs)
        else:
            flash("You don't have access to this page.", 'danger')
            return redirect(url_for('auth.index', user_id=current_user.id))
        
    return decorated_function


# Custom decorator to check if the user is an HR manager or admin   
def user_is_hr_manager_or_admin(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and (current_user.role == 'HR_MANAGER' or current_user.is_admin):
            return func(*args, **kwargs)
        else:
            flash("You don't have access to this page.", 'danger')
            return redirect(url_for('auth.index', user_id=current_user.id))
    return decorated_function

# Custom decorator to check if the user is an employee
def user_is_employee(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.role == 'EMPLOYEE':
            return func(*args, **kwargs)
        else:
            flash("You don't have access to this page.", 'danger')
            return redirect(url_for('auth.index', user_id=current_user.id))
    return decorated_function

# Custom decorator to check if the user is an employee or admin
def user_is_employee_or_admin(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and (current_user.role == 'EMPLOYEE' or current_user.is_admin):
            return func(*args, **kwargs)
        else:
            flash("You don't have access to this page.", 'danger')
            return redirect(url_for('auth.index', user_id=current_user.id))
    return decorated_function

# Custom decorator to check if the user is an employee or HR manager
def user_is_employee_or_hr_manager(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and (current_user.role == 'EMPLOYEE' or current_user.role == 'HR_MANAGER'):
            return func(*args, **kwargs)
        else:
            flash("You don't have access to this page.", 'danger')
            return redirect(url_for('auth.index', user_id=current_user.id))
    return decorated_function

# Custom decorator to check if the user is an employee, HR manager, or admin
def user_is_employee_or_hr_manager_or_admin(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and (current_user.role == 'EMPLOYEE' or current_user.role == 'HR_MANAGER' or current_user.is_admin):
            return func(*args, **kwargs)
        else:
            flash("You don't have access to this page.", 'danger')
            return redirect(url_for('auth.index', user_id=current_user.id))
    return decorated_function

# Custom decorator to check if the user is an employee of the specified company
def user_is_employee_of_company(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        company_id = kwargs.get('company_id')
        if current_user.is_authenticated and current_user.role == 'EMPLOYEE' and current_user.company_id == company_id:
            return func(*args, **kwargs)
        else:
            flash("You don't have access to this company's data.", 'danger')
            return redirect(url_for('auth.index', user_id=current_user.id))
    return decorated_function

# Custom decorator to check if the user is an HR manager of the specified company
def user_is_hr_manager_of_company(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        company_id = kwargs.get('company_id')
        if current_user.is_authenticated and current_user.role == 'HR_MANAGER' and current_user.company_id == company_id:
            return func(*args, **kwargs)
        else:
            flash("You don't have access to this company's data.", 'danger')
            return redirect(url_for('auth.index', user_id=current_user.id))
    return decorated_function

# Custom decorator to check if the user is an admin of the specified company
def user_is_admin_of_company(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        company_id = kwargs.get('company_id')
        if current_user.is_authenticated and current_user.is_admin and current_user.company_id == company_id:
            return func(*args, **kwargs)
        else:
            flash("You don't have access to this company's data.", 'danger')
            return redirect(url_for('auth.index', user_id=current_user.id))
    return decorated_function

# Custom decorator to check if the user is an employee, HR manager, or admin of the specified company
def user_is_employee_or_hr_manager_or_admin_of_company(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        company_id = kwargs.get('company_id')
        if current_user.is_authenticated and (
            (current_user.role == 'EMPLOYEE' and current_user.company_id == company_id) or
            (current_user.role == 'HR_MANAGER' and current_user.company_id == company_id) or
            (current_user.is_admin and current_user.company_id == company_id)
        ):
            return func(*args, **kwargs)
        else:
            flash("You don't have access to this company's data.", 'danger')
            return redirect(url_for('auth.index', user_id=current_user.id))
    return decorated_function




# Import necessary modules
from flask import render_template, request, jsonify, redirect, flash
from app.models import Employee, db,Company,Level,Grade,Position,Department,SalaryScale,Deduction,Benefit
import logging
from flask_login import login_required, current_user, login_user
from app.utils import user_belongs_to_company
from sqlalchemy.orm import joinedload
from flask import url_for
import app
# Import the 'employee_card' blueprint
from app.employee_card import employee_card_bp
# Import the joinedload function
from sqlalchemy.orm import joinedload

@employee_card_bp.route('/employee_card/<int:company_id>/<int:user_id>/', methods=['GET', 'POST'])
@login_required
@user_belongs_to_company
def employee_card(company_id, user_id):
    # Fetch the company for the given user_id
    company = Company.query.get(company_id)  # Replace with your actual query logic for the Company model
    positions = Position.query.all()
    departments=Department.query.all()
    grades=Grade.query.all()
    levels=Level.query.all()


    # Fetch 'employees' data for the specific company with necessary joins
    employees = Employee.query.all()

    # Construct a list of employee details
    employee_details = [
        {
            "employee_id": employee.id,
            "name": employee.name,
            "gender": employee.gender,
            "date_of_birth": employee.date_of_birth,
            "phone_num": employee.phone_num,
            "email": employee.email,
            "address": employee.address,
            "city": employee.city,
            "postal_code": employee.postal_code,
            "country": employee.country,
            "level": employee.get_level_name(),  
            "grade": employee.get_grade_name(),  
            "position": employee.get_position_name(),  
            "department": employee.get_department_name(), 
            "company": employee.get_company_name(),  
            "salary_scale": employee.salary_scale
        }
        for employee in employees
    ]

    # Render the 'employee_card_view.html' template with employee details
    template_name = 'page/employee_card.html'
    employee_card_url = url_for('employee_card.employee_card', user_id=user_id, company_id=company_id)
    return render_template(template_name, company_id=company_id, employees=employees, positions=positions,grades=grades,levels=levels,departments=departments, user_id=user_id, company=company, employee_details=employee_details, employee_card_url=employee_card_url)



@employee_card_bp.route('/add_employee/<int:company_id>/<int:user_id>', methods=['GET', 'POST'])
@login_required
@user_belongs_to_company
def add_employee(company_id, user_id):
    if request.method == 'POST':
        # Fetch names from the form fields
        position_name = request.form.get('position')
        grade_name = request.form.get('grade')
        level_name = request.form.get('level')
        department_name = request.form.get('department')

        # Fetch related instances based on names
        deductions = Deduction.get_deductions_by_company(company_id)
        benefits = Benefit.get_benefits_by_company(company_id)

        position = Position.query.filter_by(name=position_name).first()
        grade = Grade.query.filter_by(name=grade_name).first()
        level = Level.query.filter_by(name=level_name).first()
        department = Department.query.filter_by(name=department_name).first()

       
        form_data = {
            'company_id': company_id,
            'name': request.form.get('name'),
            'gender': request.form.get('gender'),
            'employee_id': request.form.get('employeeID'),
            'date_of_birth': request.form.get('date_of_birth'),
            'email': request.form.get('email'),
            'phone_num': request.form.get('phone_num'),
            'address': request.form.get('address'),
            'city': request.form.get('city'),
            'position': position,
            'grade': grade,
            'level': level,
            'department': department,
            'postal_code': request.form.get('postal_code'),
            'country': request.form.get('country'),
            'next_of_kin': request.form.get('next_of_kin'),
            'next_of_kin_phone': request.form.get('next_of_kin_phone'),
            'next_of_kin_relationship': request.form.get('next_of_kin_relationship'),
            'next_of_kin_email': request.form.get('next_of_kin_email')
        }

        new_employee = Employee(**form_data)

        db.session.add(new_employee)
        db.session.commit()
        flash('Employee added successfully', 'success')
        return redirect(url_for('dashboard.dashboard', company_id=company_id, user_id=user_id))

    return render_template('employee_card.html', company_id=company_id, user_id=user_id, deductions=deductions, benefits=benefits)

# Define the edit_employee route
@employee_card_bp.route('/<int:company_id>/edit_employee/<int:employee_id>', methods=['GET', 'POST'])
@login_required
@user_belongs_to_company
def edit_employee(company_id, employee_id):
    # Retrieve the employee to be edited
    employee = Employee.query.get_or_404(employee_id)
    deductions = Deduction.get_deductions_by_company(company_id)
    benefits = Benefit.get_benefits_by_company(company_id)
    salary_scales = SalaryScale.query.all()  # Fetch salary scales from the database


    # Check if the employee belongs to the specified company
    if employee.company_id != company_id:
        flash('Employee not found in the specified company.', 'error')
        return redirect(url_for('employee_card_view', company_id=company_id, content_id='employee_card_view'))

    if request.method == 'POST':
        # Update the employee information with data from the form
        employee.name = request.form.get('name')
        employee.gender = request.form.get('gender')
        employee.date_of_birth = request.form.get('date_of_birth')
        employee.email = request.form.get('email')
        employee.phone_num = request.form.get('phone_num')
        employee.address = request.form.get('address')
        employee.city = request.form.get('city')
        employee.postal_code = request.form.get('postal_code')
        employee.country = request.form.get('country')
        # Update additional fields as needed
        employee.department = request.form.get('department')
        employee.position = request.form.get('position')
        employee.salary_scale = request.form.get('salary_scale')
        # Update more fields as needed

        # Commit the changes to the database
        db.session.commit()

        flash('Employee information updated successfully.', 'success')

        # Redirect to the employee card view or the appropriate view
        return redirect(url_for('employee_card_view', company_id=company_id,user_id=user_id))

    # Render the form to edit the employee's information
    return render_template('dashboard.html', company_id=company_id, employee=employee,user_id=user_id, deductions=deductions, benefits=benefits,salary_scale=salary_scales)



# Define the delete_employee route
@employee_card_bp.route('/<int:company_id>/delete_employee/<int:employee_id>', methods=['POST'])
@login_required
@user_belongs_to_company
def delete_employee(company_id, employee_id):
    # Fetch the employee to be deleted
    employee = Employee.query.get_or_404(employee_id)

    # Check if the employee belongs to the specified company
    if employee.company_id != company_id:
        flash('Employee not found in the specified company.', 'error')
        return redirect(url_for('employee_card_content', company_id=company_id))

    # Delete the employee from the database
    db.session.delete(employee)
    db.session.commit()

    flash('Employee deleted successfully.', 'success')
    return redirect(url_for('employee_card_view', company_id=company_id,user_id=user_id))

@employee_card_bp.route('/<company_id>/<user_id>/content/general_info', methods=['GET'])
@login_required
@user_belongs_to_company
def general_info(company_id, user_id):
    # Fetch data for the General Info tab (employee details, such as name, gender, etc.)
    employee = Employee.query.get(user_id)
    if not employee:
        flash("Employee not found", "error")
        return redirect(url_for('dashboard.dashboard_home', company_id=company_id, user_id=user_id))

    # Render the General Info tab template
    return render_template('general_info.html', employee=employee)

# Example route code for 'employment-info' tab with additional employment-related data
@employee_card_bp.route('/<company_id>/<user_id>/content/employment_info', methods=['GET', 'POST'])
@login_required
@user_belongs_to_company
def employment_info(company_id, user_id):
    # Fetch employment-related data
    employee = Employee.query.get(user_id)  # Use user_id instead of undefined employee_id
    if employee:
        employment_data = {
            "employee_id": employee.id,
            "date_of_hire": employee.date_of_hire,
            "job_title": employee.job_title,
            "department": employee.get_department_name(),  # Use the method to get department name
            "supervisor_name": employee.supervisor_name,
            "contract_type": employee.contract_type,
            # Add more employment-related fields as needed
        }
    else:
        employment_data = {}

    # Render the template for the 'employment-info' tab
    template_name = 'employment_info.html'
    return render_template(template_name, company=company, user_id=user_id, employment_data=employment_data)


@employee_card_bp.route('/<company_id>/<user_id>/content/payroll_info', methods=['GET', 'POST'])
@login_required
@user_belongs_to_company
def payroll_info(company_id, user_id):
    # Fetch payroll-related data for the user from the database
    payroll_data = Payroll.query.filter_by(user_id=user_id, company_id=company_id).first()

    if request.method == 'POST':
        # Handle form submission and update payroll data
        if payroll_data is None:
            # If no existing payroll data, create a new record
            new_payroll_data = Payroll(
                user_id=user_id,
                company_id=company_id,
                salary=request.form.get('salary'),
                bank_account=request.form.get('bank_account'),
                tax_id=request.form.get('tax_id'),
                benefits=request.form.get('benefits')
                # Add more payroll-related data fields here
            )
            db.session.add(new_payroll_data)
        else:
            # Update the existing payroll data
            payroll_data.salary = request.form.get('salary')
            payroll_data.bank_account = request.form.get('bank_account')
            payroll_data.tax_id = request.form.get('tax_id')
            payroll_data.benefits = request.form.get('benefits')
            # Update more payroll-related data fields here

        db.session.commit()
        flash('Payroll information updated successfully', 'success')
        return redirect(url_for('dashboard.payroll_info', company_id=company_id, user_id=user_id))

    return render_template('payroll_info.html', company_id=company_id, user_id=user_id, payroll_data=payroll_data)

#paycode benefits tab route
@employee_card_bp.route('/<company_id>/<user_id>/content/benefits', methods=['GET'])
@login_required
@user_belongs_to_company
def benefits(company_id, user_id):
    # Fetch data for the Benefits tab (benefits information) from the database
    benefits = Benefit.query.filter_by(employee_id=user_id).all()
    
    if not benefits:
        flash("No benefits found for this employee.", "info")

    # Render the Benefits tab template with the retrieved data
    return render_template('benefits.html', benefits=benefits)




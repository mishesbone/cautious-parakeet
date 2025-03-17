from app import create_app, db
from app.models import (
    Level, Grade, Position, Department, Role, Permission,
    PayCode, Employee, User, Company, Attendance, LeaveRequest, PerformanceReview
)

def create_default_hr_data():
    """Create default HR data like attendance records, leave types, etc."""
    # Add default attendance records for employees (example)
    for employee in Employee.query.all():
        if not Attendance.query.filter_by(employee_id=employee.id).first():
            attendance = Attendance(employee_id=employee.id, status="Present")
            db.session.add(attendance)

    # Add default leave types
    leave_types = ['Sick Leave', 'Casual Leave', 'Annual Leave']
    for leave_type in leave_types:
        if not LeaveRequest.query.filter_by(type=leave_type).first():
            leave_request = LeaveRequest(type=leave_type)
            db.session.add(leave_request)

    # Add default performance review criteria
    review_criteria = ['Communication', 'Teamwork', 'Technical Skills', 'Punctuality']
    for criterion in review_criteria:
        if not PerformanceReview.query.filter_by(criterion=criterion).first():
            performance_review = PerformanceReview(criterion=criterion)
            db.session.add(performance_review)

    print("Default HR data created successfully.")

if __name__ == "__main__":
    # Initialize your Flask app and database
    app = create_app()
    with app.app_context():
        db.create_all()

        # Create default levels, grades, and positions
        Level.create_defaults()
        Grade.create_defaults()
        Position.create_defaults()
        Department.create_defaults()
        Role.create_defaults()

        # Fetch or create a company object by name
        company_name = 'Company A'  # Replace with your company's name
        company = Company.query.filter_by(name=company_name).first()

        if company is None:
            # Create the default company if it doesn't exist
            default_company = Company(
                name=company_name,
                num_employees=100,
                business_email='hr@companya.com',
                payment_verification_status='Verified',
                is_enabled=True
            )
            db.session.add(default_company)
            db.session.commit()
            company = default_company

        # Continue with your logic, e.g., creating default paycodes and employees
        PayCode.create_defaults(company)
        if not Employee.query.first():
            Employee.create_defaults(company)

        # Create HR-specific data
        create_default_hr_data()

        db.session.commit()
        print("Default HR data and payroll setup completed successfully.")

    app.run(debug=True)

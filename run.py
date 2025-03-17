from app import create_app, db
from flask.cli import FlaskGroup

# Create an instance of the Flask application
app = create_app()

# Create a Flask CLI Group to add custom commands
cli = FlaskGroup(create_app=create_app)

# Import your models if necessary
from app.models import (
    Level, Grade, Position, Department, Role, Permission, Company,
    PayCode, Employee, Attendance, LeaveRequest, PerformanceReview
)

# Define a custom CLI command for database initialization
@cli.command("init_db")
def initialize_database():
    """Initialize the database with default data."""
    with app.app_context():
        db.create_all()
        
        # Create default levels, grades, positions, and departments
        Level.create_defaults()
        Grade.create_defaults()
        Position.create_defaults()
        Department.create_defaults()
        Role.create_defaults()
        
        # Create default paycodes and employees for a default company
        company_name = 'Company A'
        company = Company.query.filter_by(name=company_name).first()
        if company is None:
            # Create the default company
            company = Company(
                name=company_name,
                num_employees=100,
                business_email='hr@companya.com',
                payment_verification_status='Verified',
                is_enabled=True
            )
            db.session.add(company)
            db.session.commit()

        PayCode.create_defaults(company)
        if not Employee.query.first():
            Employee.create_defaults(company)

        # Create HR-specific default data
        create_default_hr_data()

        db.session.commit()
    print("Database initialized with default data.")

def create_default_hr_data():
    """Create default HR-related data like attendance, leave types, etc."""
    # Add default attendance records for employees
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

if __name__ == '__main__':
    cli()

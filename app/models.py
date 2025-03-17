from datetime import datetime, timedelta
import secrets
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate, migrate 
import secrets
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
import uuid

# Initialize SQLAlchemy and other extensions
db = SQLAlchemy()
bcrypt = Bcrypt()


# Role model
class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    permissions = db.relationship('Permission', secondary='role_permissions', backref=db.backref('roles', lazy='dynamic'))

    def __repr__(self):
        return self.name

    @classmethod
    def create_defaults(cls):
        # Define default roles and permissions here
        default_roles = [
            {"name": "admin", "description": "Administrator role with full access to payroll management"},
            {"name": "manager", "description": "Manager role with permissions to view and manage employee data"},
            {"name": "employee", "description": "Employee role with basic permissions for self-service"},
        ]

        default_permissions = [
            {"name": "create_employee", "description": "Create new employee profiles"},
            {"name": "edit_employee", "description": "Edit employee information"},
            {"name": "delete_employee", "description": "Delete employee profiles"},
            {"name": "view_employee_details", "description": "View detailed employee information"},
            {"name": "generate_payroll", "description": "Generate payroll reports"},
            {"name": "approve_leave_requests", "description": "Approve employee leave requests"},
            {"name": "view_tax_information", "description": "Access tax-related employee data"},
            {"name": "manage_benefits", "description": "Manage employee benefits and deductions"},
            {"name": "view_payroll_reports", "description": "View various payroll reports"},
            {"name": "assign_roles", "description": "Assign roles and permissions to other users"},
            # Add more specific permissions related to your payroll system
        ]


        for role_data in default_roles:
            role = cls.query.filter_by(name=role_data["name"]).first()
            if not role:
                role = cls(**role_data)
            for permission_data in default_permissions:
                permission = Permission.query.filter_by(name=permission_data["name"]).first()
                if permission:
                    role.permissions.append(permission)
            db.session.add(role)

        db.session.commit()
        



# Define the association table for user roles
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('roles.id'))
)

# Define the association table for user permissions
user_permissions = db.Table(
    'user_permissions',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'), primary_key=True)
)

# Permission model
class Permission(db.Model):
    __tablename__ = 'permission'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))

    # Define other fields as needed

    def __repr__(self):
        return self.name

role_permissions = db.Table(
    'role_permissions',
    db.Column('role_id', db.Integer(), db.ForeignKey('roles.id')),
    db.Column('permission_id', db.Integer(), db.ForeignKey('permission.id'))
)

# User model with a relationship to roles and permissions
class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password = db.Column(db.String(100), nullable=False)
    is_enabled = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=True)
    token = db.Column(db.String(255), nullable=False, unique=True)
    token_expiration = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=False,index=True)
    email_confirmed_at = db.Column(db.DateTime)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    agree_to_terms = db.Column(db.Boolean, default=False)
    role = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    permissions = db.relationship('Permission', secondary=user_permissions, backref=db.backref('users', lazy='dynamic'))
    # Define the relationship to the companies without 'dynamic' loader


    @property
    def role_names(self):
        return [role.name for role in self.role]
        
    @staticmethod
    def get_user(user_id):
        return User.query.get(int(user_id))


    def __repr__(self):
        return f"<User {self.name}>"

    def generate_token(self):
        self.token = secrets.token_hex(32)
        self.token_expiration = datetime.utcnow() + timedelta(hours=24)
        db.session.commit()

    def has_confirmed_email(self):
        return self.email_confirmed_at is not None

    def get_id(self):
        return str(self.id)

    def set_password(self, password):
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.password = hashed_password

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def has_permission(self, permission_name):
    # Retrieve the user's roles or permissions from your database or user object
        user_permissions = self.get_permissions()  # Implements a method to get user permissions

        # Check if the user has the specified permission
        return permission_name in user_permissions
    def get_permissions(self):
        # Initialize an empty set to store user's permissions
        permissions = set()

        # Collect permissions associated with the user
        for permission in self.permissions:
            permissions.add(permission.name)

        return permissions
    # Function to set default roles and permissions for a new user
    def set_default_roles_permissions(self):
        # Set default roles for new users
        default_roles = Role.query.filter(Role.name.in_(["admin"]))  # Adjust roles as needed
        self.role.extend(default_roles)

        # Set default permissions for new users
        default_permissions = Permission.query.filter(Permission.name.in_(["assign_roles"]))  # Adjust permissions as needed
        self.permissions.extend(default_permissions)


    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def token_expired(self):
        if self.token_expiration is None:
            return True
        return datetime.utcnow() > self.token_expiration

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

# Level model
class Level(db.Model):
    __tablename__ = 'levels'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    employees = relationship('Employee', back_populates='level')

    def __repr__(self):
        return self.name

    @classmethod
    def create_defaults(cls):
        # Define default level names
        default_levels = ['Entry Level', 'Mid Level', 'Senior Level']

        # Query for existing default levels in the database
        existing_levels = cls.query.filter(cls.name.in_(default_levels)).all()

        # Create and add default levels that do not exist in the database
        for level_name in default_levels:
            if not any(level.name == level_name for level in existing_levels):
                level = cls(name=level_name)
                db.session.add(level)

        # Commit the changes to the database
        db.session.commit()


# Grade model
class Grade(db.Model):
    __tablename__ = 'grades'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    employees = relationship('Employee', back_populates='grade')
    

    def __repr__(self):
        return self.name
    
    @classmethod
    def create_defaults(cls):
        # Define default grade names (Grade 1 to 8)
        default_grades = ["Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5", "Grade 6", "Grade 7", "Grade 8"]

        # Query for existing default grades in the database
        existing_grades = cls.query.filter(cls.name.in_(default_grades)).all()

        # Create and add default grades that do not exist in the database
        for grade_name in default_grades:
            if not any(grade.name == grade_name for grade in existing_grades):
                grade = cls(name=grade_name)
                db.session.add(grade)

        # Commit the changes to the database
        db.session.commit()

# Position model
class Position(db.Model):
    __tablename__ = 'positions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))  # Add the description field
    employees = relationship('Employee', back_populates='position')
    

    def __repr__(self):
        return self.name

    @classmethod
    def create_defaults(cls):
        # Define default positions with names and descriptions
        default_positions = [
            {"name": "Manager", "description": "Operations"},
            {"name": "Technician", "description": "Enterprise IT and Networking"},
            {"name": "Support Engineer", "description": "Technical support"},
            {"name": "Information Security Officer", "description": "Data security and compliance"},
            {"name": "Accountant", "description": "Finance"},
            {"name": "Developer", "description": "Software Development"},
        ]

        # Query for existing default positions in the database
        existing_positions = cls.query.filter(cls.name.in_([p["name"] for p in default_positions])).all()

        # Create and add default positions that do not exist in the database
        for position_data in default_positions:
            if not any(position.name == position_data["name"] for position in existing_positions):
                position = cls(name=position_data["name"], description=position_data["description"])
                db.session.add(position)

        # Commit the changes to the database
        db.session.commit()

# Department model
class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False, index=True)
    employees = db.relationship('Employee', back_populates='department')

    # Create a function to create default departments
    @classmethod
    def create_defaults(cls):
        # Define default department names and descriptions
        default_departments = [
            {"name": "HR Department"},
            {"name": "Finance Department"},
            {"name": "IT Department"},
            {"name": "Sales Department"},
        ]

        # Check if departments already exist in the database
        existing_departments = cls.query.filter(cls.name.in_([d["name"] for d in default_departments])).all()

        # Create and add default departments that do not exist in the database
        for department_data in default_departments:
            if not any(department.name == department_data["name"] for department in existing_departments):
                department = cls(name=department_data["name"])
                db.session.add(department)

        # Commit the changes to the database
        db.session.commit()

    def __repr__(self):
        return self.name


# Employee model
class Employee(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True,nullable=False,index=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False,index=True) 
    name = db.Column(db.String(100), nullable=False, index=True)
    gender = db.Column(db.String(10))
    date_of_birth = db.Column(db.Date)
    phone_num = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.String(255))
    city = db.Column(db.String(50))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(50))
    salary_scale = db.Column(db.String(50),nullable=True)
    level_id = db.Column(db.Integer, db.ForeignKey('levels.id'), nullable=True)
    level = relationship('Level', back_populates='employees')
    grade_id = db.Column(db.Integer, db.ForeignKey('grades.id'), nullable=True)
    grade = relationship('Grade', back_populates='employees')
    position = relationship('Position', back_populates='employees')
    position_id = db.Column(db.Integer, db.ForeignKey('positions.id'), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))  # Updated for the 'company' table
    company = relationship('Company', back_populates='employees')
    # Define the department relationship
    department = db.relationship('Department', back_populates='employees')
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    next_of_kin = db.Column(db.String(100))
    next_of_kin_phone=db.Column(db.String(20))
    next_of_kin_relationship = db.Column(db.String(100))
    next_of_kin_email = db.Column(db.String(100))

    # Add new fields here
    bank_account = db.Column(db.String(50))
    tax_id = db.Column(db.String(20))
    benefits = db.Column(db.String(255))  # This field can be modified to match your needs
    # Define a relationship to the PayrollReporting model
    payroll_reporting = db.relationship('PayrollReporting', back_populates='employee')


    monthly_payroll = db.relationship('MonthlyPayroll', back_populates='employee')
    # Employee model Methods...
    def __repr__(self):
        return f"<Employee {self.name}>"

    def get_level_name(self):
        return self.level.name if self.level else None

    def get_grade_name(self):
        return self.grade.name if self.grade else None

    def get_position_name(self):
        return self.position.name if self.position else None

    def get_department_name(self):
        return self.department.name if self.department else None

    def get_company_name(self):
        return self.company.name if self.company else None

    def get_employee_details(self):
        details = {
            "id": self.id,
            "employee_id":self.employee_id,
            "name": self.name,
            "gender": self.gender,
            "date_of_birth": self.date_of_birth,
            "phone_num": self.phone_num,
            "email": self.email,
            "address": self.address,
            "city": self.city,
            "postal_code": self.postal_code,
            "country": self.country,
            "level": self.get_level_name(),
            "grade": self.get_grade_name(),
            "position": self.get_position_name(),
            "department": self.get_department_name(),
            "company": self.get_company_name(),
            "bank_account": self.bank_account,  
            "tax_id": self.tax_id,  
            "benefits": self.benefits,
            "monthly_payroll":self.monthly_payroll
        }
        return details


    def calculate_total_compensation(self):
        total_benefits = sum(benefit.amount for benefit in self.benefits)
        total_compensation = self.salary + total_benefits
        return total_compensation
    @classmethod
    def create_defaults(cls, company):
        unique_employee_ids = [str(uuid.uuid4()) for _ in range(2)]
        uuid_str = unique_employee_ids[0]
        first_four_characters = uuid_str[:4]
        uuid_str = unique_employee_ids[1]
        last_four_characters = uuid_str[-4:]


        departments = Department.query.all()
        positions=Position.query.all()
        levels=Level.query.all()
        grades=Grade.query.all()


        # Create default employee records associated with the provided company
        default_employees = [
            {
                "name": "John Doe",
                "employee_id": last_four_characters,
                "gender": "Male",
                "date_of_birth": datetime.utcnow(),
                "phone_num": "123-456-7890",
                "email": "john.doe@example.com",
                "address": "123 Main St",
                "city": "New York",
                "postal_code": "10001",
                "country": "USA",
                "salary_scale": "Grade A",
                "bank_account": "123456789",
                "tax_id": "TAX123",
                "benefits": "Health Insurance, Retirement Plan",
                "department": departments[0], 
                "position": positions[0],
                "grade":grades[1],
                "level":levels[1],
                "next_of_kin": "David Mishwat",
                "next_of_kin_phone": "2234567890",
                "next_of_kin_relationship":"Brother",
                "next_of_kin_email": "sneila@gmail.com",

                "company": company  # Associate the employee with the provided company
            },
            {
                "name": "Jane Smith",
                "employee_id":first_four_characters,
                "gender": "Female",
                "date_of_birth": datetime.utcnow(),
                "phone_num": "987-654-3210",
                "email": "jane.smith@example.com",
                "address": "456 Elm St",
                "city": "Los Angeles",
                "postal_code": "90002",
                "country": "USA",
                "salary_scale": "Grade B",
                "bank_account": "987654321",
                "tax_id": "TAX456",
                "benefits": "Dental Insurance, Paid Time Off",
                "department": departments[2], 
                "position": positions[5],
                "grade":grades[0],
                "level":levels[0],
                "next_of_kin": "Eucharist Mishwat",
                "next_of_kin_phone": "2234567890",
                "next_of_kin_relationship":"Brother",
                "next_of_kin_email": "sneilafacility@gmail.com",

                "company": company  # Associate the employee with the provided company
            },
            # Add more default employees associated with the company as needed
        ]
        for data in default_employees:
            employee = cls(**data)
            db.session.add(employee)

        db.session.commit()

    @classmethod
    def get_employees_in_department(cls, department_id):
        return cls.query.filter_by(department_id=department_id).all()

    @property
    def full_name(self):
        return self.name

class PayrollReporting(db.Model):
    __tablename__ = 'payroll_reporting'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    pay_period = db.Column(db.String(20), nullable=False)
    salary = db.Column(db.Float, nullable=False)
    
    
   
    tax_deduction = db.Column(db.Float, nullable=True)
    bonus = db.Column(db.Float, nullable=True)

    # Define a relationship to the Employee model
    employee = db.relationship('Employee', back_populates='payroll_reporting')

    def __repr__(self):
        return f'PayrollReporting(id={self.id}, employee_id={self.employee_id}, pay_period={self.pay_period}, salary={self.salary})'

# Company model
class Company(db.Model):
    __tablename__ = 'company'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    num_employees = db.Column(db.String(50), nullable=False)
    business_email = db.Column(db.String(100), nullable=False)
    payment_verification_status = db.Column(db.String(50), nullable=False)
    is_enabled = db.Column(db.Boolean, default=False)
    
    employees = relationship("Employee", back_populates="company")
    salary_scales = db.relationship('SalaryScale', back_populates='company')


    # Define the relationship with users
    users = db.relationship('User', backref='company', lazy=True)
    
    def __init__(self, name, num_employees, business_email, payment_verification_status, is_enabled, employees=None, salary_scales=None):
        self.name = name
        self.num_employees = num_employees
        self.business_email = business_email
        self.payment_verification_status = payment_verification_status
        self.is_enabled = is_enabled
        self.employees = employees if employees is not None else []
        self.salary_scales = salary_scales if salary_scales is not None else []


    # company methods
    @classmethod
    def create_defaults(cls, user):
        # Define new_company at the beginning of the method
        new_company = None

        # Check if 'Company A' exists in the database
        existing_company = Company.query.filter_by(name='Company A').first()

        if existing_company:
            # 'Company A' already exists in the database; handle accordingly
            print("Company A already exists in the database. You might want to update it or perform other actions.")

            # Retrieve the existing company's ID
            company_id = existing_company.id

            # Check if 'default_user_01' with email 'dave@roboteknologies.org' exists
            existing_user = User.query.filter_by(email='dave@roboteknologies.org').first()

            if existing_user:
                # 'default_user_01' already exists, update it
                existing_user.name = "Default User"  
            else:
                password="password"
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                # 'default_user_01' doesn't exist, create a new user
                default_user = User(
                    name="default_user_01",
                    email="dave@roboteknologies.org",
                    password=hashed_password,
                    is_enabled=1,
                    is_admin=1,
                    token=secrets.token_hex(32),
                    token_expiration=datetime.utcnow(),
                    is_active=1,
                    email_confirmed_at=datetime.utcnow(),
                    company_id=company_id,
                    agree_to_terms=1
                )
                
                db.session.add(default_user)

            # Commit the changes
            db.session.commit()
        else:
            # 'Company A' doesn't exist, you can proceed with the insertion
            new_company = Company(
                name='Company A',
                num_employees=100,
                business_email='dave@roboteknologies.org',
                payment_verification_status='Verified',
                is_enabled=True
            )
            new_company.employees.append(employee1)
            new_company.employees.append(employee2)
            new_company.salary_scales.append(scale1)
            new_company.salary_scales.append(scale2)


            db.session.add(new_company)

            # Check if 'default_user_01' with email 'dave@roboteknologies.org' exists
            existing_user = User.query.filter_by(email='dave@roboteknologies.org').first()

            if existing_user:
                # 'default_user_01' already exists, update it
                existing_user.name = "Updated User Name"  # Update user attributes as needed
            else:
                # 'default_user_01' doesn't exist, create a new user
                default_user = User(
                    name="default_user_01",
                    email="dave@roboteknologies.org",
                    password="password",
                    is_enabled=1,
                    is_admin=1,
                    token=secrets.token_hex(32),
                    token_expiration=datetime.utcnow(),
                    is_active=0,
                    email_confirmed_at=datetime.utcnow(),
                    company_id=new_company.id,
                    agree_to_terms=1
                )
                db.session.add(default_user)

            # Commit the changes
            db.session.commit()

            print("Company A has been added to the database.")

        return new_company  

    
    @property
    def active_users_count(self):
        return User.query.filter_by(company_id=self.id, is_active=True).count()
    
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    date = db.Column(db.Date, default=db.func.current_date())
    status = db.Column(db.String(20), nullable=False)

class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Pending')

class PerformanceReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    criterion = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    review_date = db.Column(db.Date, default=db.func.current_date())

class CurrentUser(db.Model):
    __tablename__ = 'current_users'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    sign_in_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', backref='current_users')
    company = db.relationship('Company')

    def __repr__(self):
        return f"Current user ID: {self.user_id} in company ID: {self.company_id}"

# SalaryScale model
class SalaryScale(db.Model):
    __tablename__ = 'salary_scales'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, ForeignKey('company.id'))
    position_id = db.Column(db.Integer, db.ForeignKey('positions.id'), nullable=False)
    grade_id = db.Column(db.Integer, db.ForeignKey('grades.id'), nullable=False)
    level_id = db.Column(db.Integer, db.ForeignKey('levels.id'), nullable=False)
    min_salary = db.Column(db.Float, nullable=False)
    max_salary = db.Column(db.Float, nullable=False)
    company = db.relationship('Company', back_populates='salary_scales')
    position = db.relationship('Position', backref='salary_scales', lazy=True)
    grade = db.relationship('Grade', backref='salary_scales', lazy=True)
    level = db.relationship('Level', backref='salary_scales', lazy=True)

    def __repr__(self):
        return f"<SalaryScale: Company={self.company}, Position={self.position}, Grade={self.grade}, Level={self.level}, Min Salary={self.min_salary}, Max Salary={self.max_salary}>"

# SystemAdmin model
class SystemAdmin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    permission = db.Column(db.String(255), nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='system_admins')

    #  system admin methods
    def add_system_admin(self, name, permission):
        new_admin = SystemAdmin(name=name, permission=permission, company=self.company)
        db.session.add(new_admin)
        db.session.commit()
    
    def update_system_admin(self, name, permission):
        self.name = name
        self.permission = permission
        db.session.commit()
    
    def delete_system_admin(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_system_admins_by_company(cls, company_id):
        return cls.query.filter_by(company_id=company_id).all()
        
# PayCode model
class PayCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    payroll_type = db.Column(db.String(20), nullable=False)  

    company = db.relationship('Company', backref='paycodes', lazy=True)

    def __repr__(self):
        return f"PayCode: {self.name}"

    def add_pay_code(self, code, name, payroll_type):
        new_pay_code = PayCode( name=name, payroll_type=payroll_type, company=self.company)
        db.session.add(new_pay_code)
        db.session.commit()

    def update_pay_code(self, code, name, payroll_type):
        self.name = name
        self.payroll_type = payroll_type
        db.session.commit()

    def delete_pay_code(self):
        db.session.delete(self)
        db.session.commit()
    @classmethod
    def get_pay_codes_by_company(cls, company_id):
        return cls.query.filter_by(company_id=company_id).all()


    @classmethod
    def create_defaults(cls, company):
        # Define default pay codes
        default_pay_codes = [
            {"name": "Basic", "payroll_type": "Daily"},
            { "name": "Housing", "payroll_type": "Weekly"},
            { "name": "Transport", "payroll_type": "Monthly"},
            { "name": "Pension Plan", "payroll_type": "Annual"},
        ]

        # Check if each default pay code already exists in the database
        for pay_code_data in default_pay_codes:
            existing_pay_code = cls.query.filter_by(
                name=pay_code_data["name"],
                payroll_type=pay_code_data["payroll_type"],
                company=company
            ).first()

            if not existing_pay_code:
                new_pay_code = cls(
                    name=pay_code_data["name"],
                    payroll_type=pay_code_data["payroll_type"],
                    company=company
                )
                db.session.add(new_pay_code)

        # Commit the changes to the database
        db.session.commit()


class Deduction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    code = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    method_of_computation = db.Column(db.String(20), nullable=True) 
    fixed_amount = db.Column(db.Float, nullable=True)
    percentage_of_paycode = db.Column(db.Float, nullable=True)

    @classmethod
    def add_deduction(cls, company_id, code, description, method_of_computation, fixed_amount=None, percentage_of_paycode=None):
        new_deduction = Deduction(
            company_id=company_id,
            code=code,
            description=description,
            method_of_computation=method_of_computation,
            fixed_amount=fixed_amount,
            percentage_of_paycode=percentage_of_paycode,
        )
        db.session.add(new_deduction)
        db.session.commit()

    def update_deduction(self, code, description, method_of_computation, fixed_amount=None, percentage_of_paycode=None):
        self.code = code
        self.description = description
        self.method_of_computation = method_of_computation
        self.fixed_amount = fixed_amount
        self.percentage_of_paycode = percentage_of_paycode
        db.session.commit()

    def delete_deduction(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_deductions_by_company(cls, company_id):
        return cls.query.filter_by(company_id=company_id).all()

    def __repr__(self):
        return f"Deduction: Code: {self.code}"

# Benefit model
class Benefit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    code = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    method_of_computation = db.Column(db.String(20), nullable=True)  
    fixed_amount = db.Column(db.Float, nullable=True)
    percentage_of_paycode = db.Column(db.Float, nullable=True)

    # Benefit methods
    def add_benefit(self, code, description, method_of_computation, fixed_amount, percentage_of_paycode):
        new_benefit = Benefit(
            code=code,
            description=description,
            method_of_computation=method_of_computation,
            fixed_amount=fixed_amount,
            percentage_of_paycode=percentage_of_paycode,
            company=self.company,
        )
        db.session.add(new_benefit)
        db.session.commit()

    def update_benefit(self, code, description, method_of_computation, fixed_amount, percentage_of_paycode):
        self.code = code
        self.description = description
        self.method_of_computation = method_of_computation
        self.fixed_amount = fixed_amount
        self.percentage_of_paycode = percentage_of_paycode
        db.session.commit()

    def delete_benefit(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_benefits_by_company(cls, company_id):
        return cls.query.filter_by(company_id=company_id).all()

    def __repr__(self):
        return f"Benefit:  Code: {self.code}"


# Payroll model
class Payroll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    month = db.Column(db.String(20), nullable=False)
    gross_pay = db.Column(db.Float, nullable=False)
    #  payroll methods
    def calculate_net_pay(self):
        total_deductions = self.calculate_total_deductions()
        net_pay = self.gross_pay - total_deductions
        return net_pay
    
    def calculate_total_deductions(self):
        total_deductions = 0
        for deduction in self.employee.deductions:
            total_deductions += deduction.amount
        return total_deductions
    
    @classmethod
    def generate_pay_stubs_for_month(cls, year, month):
        payrolls = cls.query.filter_by(year=year, month=month).all()
        pay_stubs = []
        for payroll in payrolls:
            pay_stub = {
                "employee_name": payroll.employee.name,
                "gross_pay": payroll.gross_pay,
                "net_pay": payroll.calculate_net_pay()
            }
            pay_stubs.append(pay_stub)
        return pay_stubs
    

    def __repr__(self):
        return f"Payroll for Employee ID {self.employee_id}, Month: {self.month}"

# PaySlip model
class PaySlip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    month = db.Column(db.String(20), nullable=False)

    # pay slip methods
    def generate_pay_slip(self):
        #logic to generate the pay slip content
        pay_slip_content = f"Pay Slip for {self.employee.name}\n"
        pay_slip_content += f"Month: {self.month}\n"
        # Include other relevant details
        return pay_slip_content

    @classmethod
    def generate_pay_slips_for_month(cls, year, month):
        pay_slips = cls.query.filter_by(year=year, month=month).all()
        return [pay_slip.generate_pay_slip() for pay_slip in pay_slips]
    

    def __repr__(self):
        return f"PaySlip for Employee ID {self.employee_id}, Month: {self.month}"

# Settings model
class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    language = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    theme = db.Column(db.String(20), nullable=True)

    def set_theme(self, theme_name):
        available_themes = ["light", "dark", "blue"]
        if theme_name in available_themes:
            self.theme = theme_name
            db.session.commit()
        else:
            raise ValueError("Invalid theme name")

    @property
    def available_languages(self):
        return ["English", "Spanish", "French", "German", "Chinese"]

    @property
    def available_locations(self):
        return ["Location1", "Location2", "Location3"]  # Add valid location names

    def __init__(self, company_id, language, location, theme="light"):
        self.company_id = company_id
        self.language = language
        self.location = location
        self.theme = theme  # Set the default theme

    def save(self):
        db.session.add(self)
        db.session.commit()

class MonthlyPayroll(db.Model):
    # Define the name of the table in the database
    __tablename__ = 'monthly_payroll'

    # Primary Key field (assuming 'id' as the primary key)
    id = db.Column(db.Integer, primary_key=True)

    # Other fields (you can add more fields as needed)
    month = db.Column(db.String(10), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    basic_salary = db.Column(db.Float, nullable=False)
    allowances = db.Column(db.Float, nullable=True)
    deductions = db.Column(db.Float, nullable=True)
    net_salary = db.Column(db.Float, nullable=False)
    # Define the relationship with Employee using a foreign key
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    employee = db.relationship('Employee', back_populates='monthly_payroll')

    def __init__(self, employee_id, month, year, basic_salary, allowances, deductions, net_salary):
        self.employee_id = employee_id
        self.month = month
        self.year = year
        self.basic_salary = basic_salary
        self.allowances = allowances
        self.deductions = deductions
        self.net_salary = net_salary

    def __repr__(self):
        return f'MonthlyPayroll(id={self.id}, employee_id={self.employee_id}, month={self.month}, year={self.year})'

# Additional model configuration
# For example, you might want to specify indexes or constraints here.


# UserCompany model
class UserCompany(db.Model):
    __tablename__ = 'user_companies'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)


    company = db.relationship('Company')

    def __repr__(self):
        return f"User: {self.user_id}, Company: {self.company_id}"

# Initialization function
def init_db():
    from app import create_app
    app = create_app()
    with app.app_context():
        db.init_app(app)
        migrate.init_app(app, db)
        # Additional models to import and create tables if needed
        db.create_all()
        db.session.commit()



        
        


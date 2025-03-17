#app/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,HiddenField, SubmitField, BooleanField, DateField, SelectField, FileField,validators
from wtforms.validators import InputRequired, Email, EqualTo, DataRequired, Optional,Length, ValidationError
from app.models import User 
from flask_wtf import FlaskForm
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models import Company 
from wtforms import SelectMultipleField, validators
from flask_wtf import FlaskForm

class RoleEditForm(FlaskForm):
    role_name = StringField('Role Name', render_kw={'class': 'form-control'})
    submit = SubmitField('Update Role', render_kw={'class': 'btn btn-primary'})



class CompanySelectionForm(FlaskForm):
    company = SelectField('Select a Company', coerce=int)
    submit = SubmitField('Submit')


class ForgotPasswordForm(FlaskForm):
    email = StringField('Email')
    submit = SubmitField('Submit')

class AdminForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    is_admin = BooleanField('Is Admin')  # Checkbox for admin privilege
    submit = SubmitField('Submit')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already taken. Please choose a different one.')

class RoleAssignmentForm(FlaskForm):
    user = SelectField('Select User', validators=[DataRequired()])
    roles = SelectMultipleField('Select Roles', validators=[DataRequired()], coerce=int)
    submit = SubmitField('Assign Roles')

    def __init__(self, user_choices, role_choices, *args, **kwargs):
        super(RoleAssignmentForm, self).__init__(*args, **kwargs)
        self.user.choices = user_choices  # Provide a list of user choices [(user_id, user_name), ...]
        self.roles.choices = role_choices  # Provide a list of role choices [(role_id, role_name), ...]

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[InputRequired()])
    submit = SubmitField('Search')


# Define the ResetPasswordForm
class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    # Remember Me field check box
    remember_me = BooleanField('Remember Me') 
    submit = SubmitField('Sign In')



# Define the ForgotPasswordForm
class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    submit = SubmitField('Submit')


class SignupForm(FlaskForm):
    name = StringField('Full Name', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[validators.DataRequired(),validators.EqualTo('confirm_password', message='Passwords must match') ])
    confirm_password = PasswordField('Confirm Password', validators=[validators.DataRequired() ])  
    agree_to_terms = BooleanField('I agree to the terms and conditions', validators=[InputRequired()])
    user_id = HiddenField('User ID')  # Add the user_id field as a HiddenField
    submit = SubmitField('Sign Up')



class CompanyRegistrationForm(FlaskForm):    
    name = StringField('Company Name', validators=[InputRequired()])
    num_employees = SelectField('Number of Employees', choices=[
        ('basic', 'Basic - 1 - 10'),
        ('standard', 'Standard - 11-50'),
        ('premium', 'Premium - 51-100'),
        ('Master-Premium', 'Premium-Master - 101-250')
    ], validators=[InputRequired()])
    business_email = StringField('Business Email', validators=[InputRequired(), Email()])
    
    # Additional fields for payment verification
    
    payment_method = SelectField('Payment Method', choices=[('credit_card', 'Credit Card'), ('check', 'Check'), ('other', 'Other')])
    payment_proof = FileField('Payment Proof (Image or Screenshot)', validators=[Optional()])
    
    submit = SubmitField('Register Company')


    def validate_business_email(self, business_email):
        company = Company.query.filter_by(business_email=business_email.data).first()
        if company:
            raise ValidationError('That email is already taken. Please choose a different one.')
        
    def validate_name(self, name):
        company = Company.query.filter_by(name=name.data).first()
        if company:
            raise ValidationError('That company name is already taken. Please choose a different one.')
        
    def validate_payment_proof(self, payment_proof):
        if self.payment_method.data == 'credit_card' and not payment_proof:
            raise ValidationError('Please upload a payment proof for your credit card.')
        
    def validate_payment_method(self, payment_method):
        if self.payment_method.data == 'credit_card' and not self.payment_proof.data:
            raise ValidationError('Please upload a payment proof for your credit card.')
        
    def validate_num_employees(self, num_employees):
        if num_employees.data not in ['basic', 'standard', 'premium', 'Master-Premium']:
            raise ValidationError('Please select a valid number of employees.')
    

class CompanyEditForm(FlaskForm):
    name = StringField('Company Name', validators=[InputRequired()])
    num_employees = SelectField('Number of Employees', choices=[
        ('basic', 'Basic - 1 - 10'),
        ('standard', 'Standard - 11-50'),
        ('premium', 'Premium - 51-100'),
        ('Master-Premium', 'Premium-Master - 101-250')
    ], validators=[InputRequired()])
    business_email = StringField('Business Email', validators=[InputRequired(), Email()])
    submit = SubmitField('Update Company')

    def validate_business_email(self, business_email):
        company = Company.query.filter_by(business_email=business_email.data).first()
        if company:
            raise ValidationError('That email is already taken. Please choose a different one.')
        
    def validate_name(self, name):
        company = Company.query.filter_by(name=name.data).first()
        if company:
            raise ValidationError('That company name is already taken. Please choose a different one.')
        
    def validate_num_employees(self, num_employees):
        if num_employees.data not in ['basic', 'standard', 'premium', 'Master-Premium']:
            raise ValidationError('Please select a valid number of employees.')
        
    
class CompanyDeleteForm(FlaskForm):
    submit = SubmitField('Delete Company')
    

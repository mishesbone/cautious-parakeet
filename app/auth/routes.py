#app/auth/routes.py
from flask import render_template, flash, redirect, url_for, request, session  
from flask_login import login_user, logout_user, login_required, current_user
from . import auth_bp
from ..forms import LoginForm, SignupForm, ForgotPasswordForm, CompanyRegistrationForm
from ..models import User, db, CurrentUser,Role
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User, db, Company,UserCompany,PayCode
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime  
from flask_mail import Message  
import stripe
from stripe.error import CardError, InvalidRequestError, AuthenticationError, APIConnectionError, StripeError
from flask import current_app as app
from app.config import Config
from flask import Flask, request, jsonify
from app import mail
from app import bcrypt
from sqlalchemy.exc import IntegrityError  
import secrets



# Initialize Stripe with the secret key from Config
stripe.api_key = Config.STRIPE_SECRET_KEY


@auth_bp.route('/')
def index():
    return render_template('index.html')


@auth_bp.route('/signin', methods=['GET', 'POST'])
def signin():
    user = current_user
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.check_password(form.password.data) and user.is_enabled:
            # Log in the user
            login_user(user)

            # Update user's last login timestamp and is_active attribute
            user.is_active = True
            db.session.commit()
            user_id = user.id

            flash('Logged in successfully!', 'success')

            return redirect(url_for('dashboard.user_dashboard', user_id=user.id))

        # If the user's account is disabled
        if user and not user.is_enabled:
            email = form.email.data
            user_id = user.id

            # Resend the verification email
            send_verification_email(email, user_id)

            flash('Verification email sent to your email. Please check your email to verify your account.', 'success')

        flash('Invalid Email or password. Please try again.', 'danger')

    return render_template('signin.html', form=form, user=user)

def send_verification_email(email, user_id):
    msg = Message('Verify Your Email', sender='mishesbone@roboteknologies.org', recipients=[email])
    verify_link = url_for('auth.verify_email', token=user.token, user_id=user_id, _external=True)
    msg.body = f'Click the link to verify your email: {verify_link}'
    mail.send(msg)
 

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        agree_to_terms = form.agree_to_terms.data

        # Check if a user with the same name or email already exists
        existing_user = User.query.filter_by(name=name).first()
        existing_user_email = User.query.filter_by(email=email).first()

        if existing_user:
            flash('User already exists. Please register a different user.', 'danger')
        elif existing_user_email:
            flash('Email address is already registered. Please use a different email.', 'danger')
        else:
            # Generate a token for the user
            user = User(
                name=name,
                email=email,
                password=bcrypt.generate_password_hash(password).decode('utf-8'),
                email_confirmed_at=None,
                agree_to_terms=agree_to_terms
            )
            # Create some roles or retrieve existing ones
            role_employee = Role.query.filter_by(name='employee').first()
            role_manager = Role.query.filter_by(name='manager').first()

            user.generate_token()  # Make sure this method assigns a token to the user
            user.set_default_roles_permissions()
            user.role.extend([role_employee, role_manager])
            db.session.add(user)
            db.session.commit()

            # Send verification email
            msg = Message('Verify Your Email', sender='mishesbone@roboteknologies.org', recipients=[email])
            verify_link = url_for('auth.verify_email', token=user.token, user_id=user.id, _external=True)
            msg.body = f'Click the link to verify your email: {verify_link}'
            mail.send(msg)

            flash('Account created successfully! Please check your email to verify your account.', 'success')

            # Redirect to the signup_success page with the correct user ID
            return redirect(url_for('auth.signup_success', user_id=user.id))

    return render_template('signup.html', form=form)



@auth_bp.route('/verify_email/<token>/<int:user_id>', methods=['GET'])
def verify_email(token, user_id):
    # Find the user by the token
    user = User.query.filter_by(token=token).first()

    if user:
        try:
            # If the user is found, update the email_confirmed_at field and remove the token
            user.email_confirmed_at = datetime.utcnow()
            user.is_enabled = True
            db.session.commit()
            flash('Email verification successful. You can now log in.', 'success')
        except IntegrityError as e:
            db.session.rollback()
            flash('An error occurred during email verification. Please try again later.', 'danger')
            app.logger.error(f'IntegrityError during email verification: {e}')
    else:
        flash('Invalid email verification token. Please request a new one.', 'danger')

    return redirect(url_for('auth.register_company', user_id=user_id))


@auth_bp.route('/signup_success/<int:user_id>')
def signup_success(user_id):
    # Retrieve the flash message from the session
    flash_message = session.pop('flash_message', None)
    
    return render_template('signup_success.html', user_id=user_id, flash_message=flash_message)

from flask_login import current_user

@auth_bp.route('/register_company/<int:user_id>', methods=['GET', 'POST'])
def register_company(user_id):
    form = CompanyRegistrationForm()
    user = User.query.get(user_id)  # Fetch the user from the database using user_id

    if form.validate_on_submit():
        company_name = form.name.data
        num_employees = form.num_employees.data
        business_email = form.business_email.data
        payment_method = form.payment_method.data

        if payment_method == 'credit_card':
            try:
                # Set the current user here:
                login_user(user)
                # Create a Payment Intent for credit card payment
                payment_intent = stripe.PaymentIntent.create(
                    amount=5000,  # Amount in cents
                    currency='usd',
                )
                return render_template('payment.html', publishable_key='pk_test_51NfBipDjqt0tSwndxZeRkCcmHI53j7gjlQQLVQOZhgsBL2r9iHpbdM8EFgmvOy3Ok31SvaKU7dPHfRtUdIJqEwwh00R2m4VClB', client_secret=payment_intent.client_secret)
            except stripe.error.StripeError as e:
                flash(f'Payment failed: {e}', 'error')
                return redirect(url_for('auth.signin'))  # Redirect to sign-in page

        elif payment_method in ('check', 'other'):
            try:
                # Set the current user here:
                login_user(user)
                # Process payment method 'check' or 'other'
                payment_proof = form.payment_proof.data
                payment_verification_status = 'Pending verification'

                # Check if a company with the same name already exists
                existing_company = Company.query.filter_by(name=company_name).first()

                if existing_company:
                    flash('Company with this name already exists. Please choose a different name.', 'danger')
                else:
                    # Send an acknowledgement email
                    acknowledgement_subject = 'Payment Proof Upload Acknowledgement'
                    acknowledgement_recipient = business_email
                    acknowledgement_msg = Message(subject=acknowledgement_subject, recipients=[acknowledgement_recipient])
                    acknowledgement_msg.body = "Thank you for uploading your payment proof. Your submission is being processed for verification. You will receive an email once your payment has been approved."
                    mail.send(acknowledgement_msg)

                    # Create a new company object
                    company = create_company(company_name, num_employees, business_email, payment_verification_status)
                    user_company = UserCompany(user_id=user.id, company_id=company.id)
                    



                    # Update user's company_id and assign the admin role
                    update_user_info(current_user, company)

                    flash('Company registered successfully! You are now assigned the admin role.', 'success')
                    return redirect(url_for('auth.signin'))  # Redirect to the sign-in page

            except Exception as e:
                flash(f'An error occurred while processing the payment: {e}', 'error')
                app.logger.error(str(e))
                return redirect(url_for('auth.signin'))  # Redirect to the sign-in page

    return render_template('register_company.html', form=form, user_id=user.id)

def create_company(name, num_employees, business_email, payment_method):
    payment_verification_status = 'Pending verification'

    # Create a new company object
    company = Company(
        name=name,
        num_employees=num_employees,
        business_email=business_email,
        payment_verification_status=payment_verification_status,
        is_enabled=False,
    )

    # Save the company object to the database
    db.session.add(company)
    db.session.commit()
    PayCode.create_defaults(company)

    return company

def update_user_info(user, company):
    user.company_id = company.id  # Assuming company.id is the primary key of the company
    user = User.query.get(user.id)

    # Now, you might have a table or attribute like 'user_roles' that associates roles with users
    admin_role = Role.query.filter_by(name='admin').first()  # Replace 'admin' with your desired role name
    if admin_role:
        user.role.append(admin_role)  # Assign the admin role to the user

    db.session.commit()


@auth_bp.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    form_data = request.form
    price_id = form_data.get('price_id')  # Get the price ID from the form data

    session = stripe.checkout.Session.create(
        line_items=[
            {
                'price': price_id,
                'quantity': 1,
            },
        ],
        mode='payment',
        success_url=url_for('success', _external=True),
        cancel_url=url_for('cancel', _external=True),
    )
    return redirect(session.url, code=303)

@auth_bp.route('/process_payment', methods=['POST'])
def process_payment():
    # Retrieve the payment method ID from the request
    payment_method_id = request.json.get('payment_method_id')

    # Use the payment method ID to confirm and complete the payment using Stripe API
    # You would typically have the Stripe API logic here to confirm the payment

    # Replace the following with your actual payment processing logic
    #  you would use Stripe API to confirm the payment
    # and return a response indicating success or failure
    try:
        # Retrieve the payment method ID from the request
        payment_method_id = request.json.get('payment_method_id')

        # Use the payment method ID to confirm the payment using Stripe API
        # Replace the following with your actual Stripe API code to confirm the payment
        # For example, you can use `stripe.PaymentIntent.confirm` to confirm the payment
        intent = stripe.PaymentIntent.confirm(
            payment_method=payment_method_id,
            payment_method_types=['card','sepa_debit', 'ideal','google_pay','apple_pay'],
        )

        # Check if the payment was successful
        if intent.status == 'succeeded':
            # Payment was successful, you can update your database or perform other actions here
            return jsonify({'success': True})
        else:
            # Payment failed
            return jsonify({'success': False, 'error_message': 'Payment failed'})

    except Exception as e:
        # Handle exceptions and errors
        return jsonify({'success': False, 'error_message': str(e)})

@auth_bp.route('/signup_success/<int:user_id>', methods=['GET', 'POST'])
@login_required
def success(user_id):
    company_id = current_user.company_id

    company = Company.query.get(company_id)

    # Update the payment verification status
    company.payment_verification_status = 'Verified'
    db.session.commit()

    flash_message = 'Payment verified successfully!'  # Define flash_message

    return render_template('payment_success.html', user_id=user_id, flash_message=flash_message)


@auth_bp.route('/cancel')
def cancel():
    flash('Payment was canceled.', 'warning')
    return render_template('cancel.html')

@auth_bp.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated:
        # Mark the user as signed out
        current_user.is_active = False

        # Find the corresponding CurrentUser record and delete it
        current_user_record = CurrentUser.query.filter_by(user=current_user, company=current_user.company).first()
        if current_user_record:
            db.session.delete(current_user_record)
            db.session.commit()

        # Logout the user (if using Flask-Login)
        logout_user()
   
    flash('You have been logged out', 'success')
    return redirect(url_for('auth.index'))

def generate_reset_token():
    # Generate a unique reset token
    return secrets.token_urlsafe(32)


def send_password_reset_email(user):
    # Generate a unique reset token (you can use a library like secrets)
    reset_token = generate_reset_token()

    # Save the reset token for the user (e.g., in the database)
    user.reset_token = reset_token
    db.session.commit()

    # Create an email message
    msg = Message('Password Reset Instructions', sender='mishesbone@roboteknologies.org', recipients=[user.email])
    msg.body = f"Please click the following link to reset your password: {url_for('auth.reset_password', token=reset_token, _external=True)}"

    # Send the email
    mail.send(msg)


@auth_bp.route('/forgot_password', methods=['GET', 'POST'], endpoint='forgot_password')
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Generate a unique reset token and send it to the user via email
            # Implement your email sending logic here
            send_password_reset_email(user)

            flash('Password reset instructions have been sent to your email.', 'success')
            return redirect(url_for('auth.signin'))
        else:
            flash('No user found with that email address.', 'danger')
    return render_template('forgot_password.html', form=form)

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Verify the token and find the user associated with it
    user = User.verify_password_reset_token(token)
    if not user:
        flash('Invalid or expired reset link. Please request a new one.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        user.password = hashed_password
        db.session.commit()

        flash('Your password has been reset. You can now log in with your new password.', 'success')
        return redirect(url_for('auth.signin'))
    
    return render_template('reset_password.html', form=form)



@auth_bp.route('/generate_invite', methods=['GET', 'POST'])
@login_required
def generate_invite():
    if current_user.role != 'admin':
        flash('You do not have permission to generate invitation links.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Extract email addresses entered by the admin
        emails = request.form.get('email')
        email_list = [email.strip() for email in emails.split(',')]

        if not email_list:
            flash('Please enter at least one email address.', 'danger')
        else:
            for email in email_list:
                # Generate a unique token/link for each email address
                invitation_token = generate_unique_token()

                # Set the expiration date for the invitation (e.g., 7 days from now)
                expiration_date = datetime.utcnow() + timedelta(days=7)

                # Store the invitation token and metadata in the database
                invitation = Invitation(token=invitation_token, role='user', expiration_date=expiration_date, email=email)
                db.session.add(invitation)
                db.session.commit()
                # Send an email with the invitation link
                mail.send(email, invitation_token)

            flash(f'Invitation links generated successfully and sent to the specified email addresses.', 'success')

    return render_template('generate_invite.html')
from flask import Blueprint, render_template, request, jsonify, redirect, flash,url_for
from app.models import Settings,User
from app.utils import user_belongs_to_company
from flask_login import login_url,login_required,current_user
from app.settings import settings_bp

@settings_bp.route('/<int:company_id>/<int:user_id>', methods=['GET'])
@login_required
@user_belongs_to_company
def settings(company_id, user_id):
    # Load the user based on user_id
    user = User.query.get(user_id)

    # Retrieve the company-specific settings for the user
    settings_data = Settings.query.filter_by(company_id=company_id).first()

    if settings_data:
        # The settings_data variable contains the settings for the user
        user_language = settings_data.language
        user_location = settings_data.location
        user_theme = settings_data.theme

        # Render the 'settings.html' template with the settings data
        template_name = 'page/settings.html'
        return render_template(template_name, user=user, settings_data=settings_data, user_language=user_language, user_location=user_location, user_theme=user_theme)
    else:
        # Handle the case where no settings are found for the user
        flash("Settings not found for this user.", "danger")
        return redirect(url_for('settings.settings_error', company_id=company_id, user_id=user_id))

@settings_bp.route('/<int:company_id>/<int:user_id>/error', methods=['GET'])
def settings_error(company_id, user_id):
    error_description = request.args.get('error_description', 'An error occurred while processing your request.')
    return render_template('error.html', company_id=company_id, user_id=user_id, error_description=error_description), 500

@settings_bp.route('/<int:company_id>/<int:user_id>/update', methods=['POST'])
@login_required
@user_belongs_to_company
def update_settings(company_id, user_id):
    language = request.form.get('language')
    location = request.form.get('location')
    theme = request.form.get('theme')

    # Find the user's specific settings record based on company_id and user_id
    settings = Settings.query.filter_by(company_id=company_id).filter_by(user_id=user_id).first()

    if settings:
        settings.language = language
        settings.location = location
        settings.set_theme(theme)  # Use the set_theme method to set the theme

        db.session.commit()
        flash('Settings updated successfully', 'success')
    else:
        flash('Settings not found for this user.', 'danger')

    return redirect(url_for('settings.settings', company_id=company_id, user_id=user_id))

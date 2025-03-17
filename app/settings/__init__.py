from flask import Blueprint, render_template, request, jsonify, redirect, flash


settings_bp = Blueprint('settings', __name__,url_prefix='/settings', template_folder='../templates/page', static_folder='../static')


from app.settings import routes
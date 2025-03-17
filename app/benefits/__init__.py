from flask import Blueprint, render_template, request, jsonify, redirect, flash


benefits_bp = Blueprint('benefits', __name__,url_prefix='/benefits', template_folder='../templates/page', static_folder='../static')


from app.benefits import routes
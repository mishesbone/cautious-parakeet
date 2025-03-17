from flask import Blueprint, render_template, request, jsonify, redirect, flash


positions_bp = Blueprint('positions', __name__,url_prefix='/positions', template_folder='../templates/page', static_folder='../static')


from app.positions import routes
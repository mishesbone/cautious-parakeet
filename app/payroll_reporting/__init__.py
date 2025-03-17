from flask import Blueprint, render_template, request, jsonify, redirect, flash


payroll_reporting_bp = Blueprint('payroll_reporting', __name__,url_prefix='/payroll_reporting', template_folder='../templates/page', static_folder='../static')


from app.payroll_reporting import routes
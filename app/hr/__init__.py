from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, Attendance, LeaveRequest, PerformanceReview, Employee

# Create a Blueprint for HR management
hr_bp = Blueprint('hr', __name__, url_prefix='/hr')

from . import routes
from flask import flash, redirect, render_template, request, url_for
from app.hr import hr_bp
from app.models import Attendance, LeaveRequest, PerformanceReview
from app.models import db

# Attendance Management
@hr_bp.route('/attendance', methods=['GET'])
def view_attendance():
    attendance_records = Attendance.query.all()
    return render_template('hr/attendance.html', records=attendance_records)

@hr_bp.route('/attendance/add', methods=['POST'])
def add_attendance():
    employee_id = request.form['employee_id']
    status = request.form['status']
    attendance = Attendance(employee_id=employee_id, status=status)
    db.session.add(attendance)
    db.session.commit()
    flash('Attendance record added successfully.')
    return redirect(url_for('hr.view_attendance'))

# Leave Requests Management
@hr_bp.route('/leave-requests', methods=['GET'])
def view_leave_requests():
    leave_requests = LeaveRequest.query.all()
    return render_template('hr/leave_requests.html', requests=leave_requests)

@hr_bp.route('/leave-requests/add', methods=['POST'])
def add_leave_request():
    employee_id = request.form['employee_id']
    leave_type = request.form['type']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    leave_request = LeaveRequest(employee_id=employee_id, type=leave_type, start_date=start_date, end_date=end_date)
    db.session.add(leave_request)
    db.session.commit()
    flash('Leave request added successfully.')
    return redirect(url_for('hr.view_leave_requests'))

# Performance Reviews Management
@hr_bp.route('/performance-reviews', methods=['GET'])
def view_performance_reviews():
    reviews = PerformanceReview.query.all()
    return render_template('hr/performance_reviews.html', reviews=reviews)

@hr_bp.route('/performance-reviews/add', methods=['POST'])
def add_performance_review():
    employee_id = request.form['employee_id']
    criterion = request.form['criterion']
    score = request.form['score']
    review = PerformanceReview(employee_id=employee_id, criterion=criterion, score=score)
    db.session.add(review)
    db.session.commit()
    flash('Performance review added successfully.')
    return redirect(url_for('hr.view_performance_reviews'))
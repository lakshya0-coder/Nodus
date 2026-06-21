"""Admin interface routes."""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from datetime import date
from app.models import db
from app.models.booking import Booking
from app.models.order import Order
from app.models.menu import MenuItem, MenuCategory

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
@login_required
def check_admin():
    if not current_user.is_staff:
        return redirect(url_for('public.home'))

@admin_bp.route('/')
@admin_bp.route('/dashboard')
def dashboard():
    """Admin dashboard."""
    today = date.today()
    
    # Simple stats
    todays_bookings = Booking.query.filter_by(date=today, status='confirmed').count()
    todays_orders = Order.query.filter(db.func.date(Order.created_at) == today).count()
    
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    upcoming_bookings = Booking.query.filter(Booking.date >= today, Booking.status == 'confirmed').order_by(Booking.date, Booking.time_slot).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         todays_bookings=todays_bookings,
                         todays_orders=todays_orders,
                         recent_orders=recent_orders,
                         upcoming_bookings=upcoming_bookings)

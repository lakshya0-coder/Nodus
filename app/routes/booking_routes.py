"""Booking page routes."""
from flask import Blueprint, render_template, session, request
from app.models.setting import Setting
from app.models.prediction import DemandPrediction
from datetime import date, timedelta

booking_bp = Blueprint('booking_page', __name__)


@booking_bp.route('/booking')
def booking():
    """Slot booking page."""
    lang = session.get('lang', request.cookies.get('lang', 'en'))

    open_hour = int(Setting.get('open_hour', '8'))
    close_hour = int(Setting.get('close_hour', '22'))

    # Generate time slots
    time_slots = []
    for hour in range(open_hour, close_hour):
        slot = f"{hour:02d}:00-{hour+1:02d}:00"
        time_slots.append({
            'value': slot,
            'label': f"{hour:02d}:00 - {hour+1:02d}:00"
        })

    # Get today's predictions
    today = date.today()
    predictions = DemandPrediction.query.filter(
        DemandPrediction.date >= today,
        DemandPrediction.date < today + timedelta(days=7)
    ).all()

    predictions_dict = {}
    for p in predictions:
        key = f"{p.date.isoformat()}_{p.time_slot}"
        predictions_dict[key] = {
            'occupancy': p.predicted_occupancy,
            'label': p.predicted_label,
            'bookings': p.predicted_bookings
        }

    return render_template('booking.html',
                         time_slots=time_slots,
                         predictions=predictions_dict,
                         capacity=int(Setting.get('total_capacity', '30')))

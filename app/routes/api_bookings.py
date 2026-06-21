"""Booking API endpoints."""
from flask import Blueprint, request, jsonify
from app.models import db
from app.models.booking import Booking
from app.models.setting import Setting
from app.models.prediction import DemandPrediction
from app.routes.auth import staff_required
from datetime import datetime, date, timedelta

api_bookings_bp = Blueprint('api_bookings', __name__)


@api_bookings_bp.route('', methods=['GET'])
@staff_required
def list_bookings():
    """List bookings with optional filters."""
    status = request.args.get('status')
    date_str = request.args.get('date')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Booking.query.order_by(Booking.date.desc(), Booking.time_slot)

    if status:
        query = query.filter_by(status=status)
    if date_str:
        try:
            filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            query = query.filter_by(date=filter_date)
        except ValueError:
            pass

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'bookings': [b.to_dict() for b in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@api_bookings_bp.route('', methods=['POST'])
def create_booking():
    """Create a new booking."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    required_fields = ['date', 'time_slot', 'customer_name']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    try:
        booking_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    # Check if date is not in the past
    if booking_date < date.today():
        return jsonify({'error': 'Cannot book for past dates'}), 400

    # Check capacity for this slot
    capacity = int(Setting.get('total_capacity', '30'))
    existing_guests = db.session.query(db.func.sum(Booking.guest_count)).filter_by(
        date=booking_date,
        time_slot=data['time_slot'],
        status='confirmed'
    ).with_for_update().scalar() or 0
    
    guest_count = data.get('guest_count', 1)

    if existing_guests + guest_count > capacity:
        return jsonify({'error': 'This slot is full. Please choose another time.'}), 409

    # Create booking
    booking = Booking(
        booking_ref=Booking.generate_ref(booking_date),
        customer_name=data['customer_name'],
        customer_email=data.get('customer_email', ''),
        customer_phone=data.get('customer_phone', ''),
        date=booking_date,
        time_slot=data['time_slot'],
        guest_count=guest_count,
        seating_preference=data.get('seating_preference', 'any'),
        status='confirmed',
        notes=data.get('notes', '')
    )

    db.session.add(booking)
    db.session.commit()

    return jsonify({
        'success': True,
        'booking': booking.to_dict(),
        'message': 'Booking confirmed successfully!'
    }), 201


@api_bookings_bp.route('/availability', methods=['GET'])
def check_availability():
    """Check slot availability for a given date."""
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({'error': 'Date parameter required'}), 400

    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    capacity = int(Setting.get('total_capacity', '30'))
    open_hour = int(Setting.get('open_hour', '8'))
    close_hour = int(Setting.get('close_hour', '22'))

    # Group bookings to prevent N+1 queries
    bookings_summary = db.session.query(
        Booking.time_slot, db.func.sum(Booking.guest_count)
    ).filter_by(
        date=target_date, status='confirmed'
    ).group_by(Booking.time_slot).all()
    booked_by_slot = dict(bookings_summary)

    # Group predictions to prevent N+1 queries
    preds = DemandPrediction.query.filter_by(date=target_date).all()
    pred_by_slot = {p.time_slot: p for p in preds}

    slots = []
    for hour in range(open_hour, close_hour):
        time_slot = f"{hour:02d}:00-{hour+1:02d}:00"

        booked_guests = int(booked_by_slot.get(time_slot, 0))
        available_seats = max(0, capacity - booked_guests)

        prediction = pred_by_slot.get(time_slot)

        slot_data = {
            'time_slot': time_slot,
            'label': f"{hour:02d}:00 - {hour+1:02d}:00",
            'booked': booked_guests,
            'available': available_seats,
            'total_capacity': capacity,
            'is_full': available_seats <= 0,
        }

        if prediction:
            slot_data['predicted_label'] = prediction.predicted_label
            slot_data['predicted_occupancy'] = prediction.predicted_occupancy
        else:
            slot_data['predicted_label'] = 'moderate'
            slot_data['predicted_occupancy'] = 0.3

        slots.append(slot_data)

    return jsonify({
        'date': date_str,
        'slots': slots,
        'capacity': capacity
    })


@api_bookings_bp.route('/lookup', methods=['GET'])
def lookup_booking():
    """Look up a booking by reference."""
    ref = request.args.get('ref', '').strip()
    if not ref:
        return jsonify({'error': 'Booking reference required'}), 400

    booking = Booking.query.filter_by(booking_ref=ref).first()
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    return jsonify({'booking': booking.to_dict()})


@api_bookings_bp.route('/<int:booking_id>', methods=['PATCH'])
@staff_required
def update_booking(booking_id):
    """Update booking status."""
    booking = Booking.query.get_or_404(booking_id)
    data = request.get_json()

    if 'status' in data:
        booking.status = data['status']
    if 'notes' in data:
        booking.notes = data['notes']
    if 'guest_count' in data:
        booking.guest_count = data['guest_count']

    db.session.commit()
    return jsonify({'success': True, 'booking': booking.to_dict()})


@api_bookings_bp.route('/<int:booking_id>', methods=['DELETE'])
@staff_required
def cancel_booking(booking_id):
    """Cancel a booking."""
    booking = Booking.query.get_or_404(booking_id)
    booking.status = 'cancelled'
    db.session.commit()
    return jsonify({'success': True, 'message': 'Booking cancelled'})

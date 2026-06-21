from app.models import db
from datetime import datetime
import json


class DemandPrediction(db.Model):
    """Predicted demand/occupancy for a given date and time slot."""
    __tablename__ = 'demand_predictions'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time_slot = db.Column(db.String(20), nullable=False)  # e.g., "10:00-11:00"
    predicted_occupancy = db.Column(db.Float, default=0.0)  # 0.0 to 1.0 (percentage)
    predicted_bookings = db.Column(db.Integer, default=0)
    predicted_label = db.Column(db.String(20), default='quiet')  # busy, moderate, quiet
    model_version_id = db.Column(db.Integer, db.ForeignKey('model_versions.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    model_version = db.relationship('ModelVersion', backref='predictions')

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'time_slot': self.time_slot,
            'predicted_occupancy': round(self.predicted_occupancy, 2),
            'predicted_bookings': self.predicted_bookings,
            'predicted_label': self.predicted_label,
            'model_version': self.model_version.version_number if self.model_version else 'rule-based',
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ModelVersion(db.Model):
    """ML model version tracking."""
    __tablename__ = 'model_versions'

    id = db.Column(db.Integer, primary_key=True)
    version_number = db.Column(db.String(20), nullable=False)  # e.g., "v1.0", "v1.1"
    trained_at = db.Column(db.DateTime, default=datetime.utcnow)
    training_data_count = db.Column(db.Integer, default=0)
    accuracy_metrics = db.Column(db.Text, default='{}')  # JSON: {"mae": 0.1, "rmse": 0.15}
    status = db.Column(db.String(20), default='active')  # active, retired, failed
    model_file_path = db.Column(db.String(300), default='')
    notes = db.Column(db.Text, default='')

    def get_metrics(self):
        try:
            return json.loads(self.accuracy_metrics) if self.accuracy_metrics else {}
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_metrics(self, metrics_dict):
        self.accuracy_metrics = json.dumps(metrics_dict)

    def to_dict(self):
        return {
            'id': self.id,
            'version_number': self.version_number,
            'trained_at': self.trained_at.isoformat() if self.trained_at else None,
            'training_data_count': self.training_data_count,
            'accuracy_metrics': self.get_metrics(),
            'status': self.status,
            'notes': self.notes
        }

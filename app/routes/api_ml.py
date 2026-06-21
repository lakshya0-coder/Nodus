"""ML Prediction API endpoints."""
from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.routes.auth import staff_required
from app.models.prediction import DemandPrediction, ModelVersion
from app.services.ml_predictor import demand_predictor
from app.services.scheduler import get_scheduler_status, trigger_retrain

api_ml_bp = Blueprint('api_ml', __name__)


@api_ml_bp.route('/predictions', methods=['GET'])
@staff_required
def get_predictions():
    """Get demand predictions."""
    predictions = demand_predictor.get_weekly_predictions()
    return jsonify({'predictions': predictions})


@api_ml_bp.route('/models', methods=['GET'])
@staff_required
def list_models():
    """List all model versions."""
    models = ModelVersion.query.order_by(ModelVersion.trained_at.desc()).all()
    return jsonify({
        'models': [m.to_dict() for m in models],
        'active_model': next((m.to_dict() for m in models if m.status == 'active'), None)
    })


@api_ml_bp.route('/retrain', methods=['POST'])
@staff_required
def retrain_model():
    """Trigger manual model retraining."""
    result = demand_predictor.train()
    return jsonify(result)


@api_ml_bp.route('/scheduler/status', methods=['GET'])
@staff_required
def scheduler_status():
    """Get scheduler status."""
    return jsonify(get_scheduler_status())


@api_ml_bp.route('/generate-predictions', methods=['POST'])
@staff_required
def generate_predictions():
    """Generate/refresh predictions."""
    demand_predictor._generate_rule_based_predictions()
    return jsonify({'success': True, 'message': 'Predictions generated'})

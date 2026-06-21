"""
ML Demand Predictor — Forecasts cafe occupancy using historical booking data.
Uses Gradient Boosting with weekly auto-retraining.
"""
import os
import json
from datetime import datetime, timedelta, date
import traceback

try:
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    import joblib
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False


class DemandPredictor:
    """ML-based demand/occupancy predictor for cafe bookings."""

    def __init__(self, app=None):
        self.app = app
        self.model = None
        self.model_dir = None

    def init_app(self, app):
        self.app = app
        self.model_dir = app.config.get('ML_MODEL_DIR', 'ml/models')
        os.makedirs(self.model_dir, exist_ok=True)
        self._load_active_model()

    def _load_active_model(self):
        """Load the currently active model from disk."""
        if not ML_AVAILABLE:
            return

        from app.models.prediction import ModelVersion
        try:
            active = ModelVersion.query.filter_by(status='active').first()
            if active and active.model_file_path and os.path.exists(active.model_file_path):
                self.model = joblib.load(active.model_file_path)
        except Exception as e:
            print(f"Could not load ML model: {e}")

    def _get_booking_data(self):
        """Extract booking history as a DataFrame."""
        from app.models.booking import Booking
        from app.models.setting import Setting

        bookings = Booking.query.filter(
            Booking.status.in_(['confirmed', 'completed'])
        ).all()

        if not bookings:
            return None

        capacity = int(Setting.get('total_capacity', '30'))

        records = []
        for b in bookings:
            if b.date and b.time_slot:
                try:
                    hour = int(b.time_slot.split(':')[0])
                except (ValueError, IndexError):
                    hour = 10  # default

                records.append({
                    'date': b.date,
                    'hour': hour,
                    'day_of_week': b.date.weekday(),  # 0=Mon, 6=Sun
                    'is_weekend': 1 if b.date.weekday() >= 5 else 0,
                    'month': b.date.month,
                    'guest_count': b.guest_count or 1,
                    'week_of_year': b.date.isocalendar()[1],
                })

        if not records:
            return None

        df = pd.DataFrame(records)

        # Aggregate bookings per date+hour slot
        grouped = df.groupby(['date', 'hour']).agg({
            'guest_count': 'sum',
            'day_of_week': 'first',
            'is_weekend': 'first',
            'month': 'first',
            'week_of_year': 'first'
        }).reset_index()

        # Calculate occupancy as fraction of capacity
        grouped['occupancy'] = (grouped['guest_count'] / capacity).clip(0, 1)

        return grouped

    def train(self):
        """Train the demand prediction model."""
        if not ML_AVAILABLE:
            return {'success': False, 'error': 'ML libraries not available'}

        from app.models import db
        from app.models.prediction import ModelVersion, DemandPrediction
        from app.models.setting import Setting

        try:
            df = self._get_booking_data()

            min_bookings = int(Setting.get('ml_min_bookings', '50'))

            if df is None or len(df) < min_bookings:
                # Not enough data — generate rule-based predictions
                self._generate_rule_based_predictions()
                return {
                    'success': True,
                    'message': f'Not enough data for ML training ({len(df) if df is not None else 0} records, need {min_bookings}). Using rule-based predictions.',
                    'method': 'rule-based'
                }

            # Features and target
            features = ['hour', 'day_of_week', 'is_weekend', 'month', 'week_of_year']
            X = df[features]
            y = df['occupancy']

            # Train-test split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Train Gradient Boosting model
            model = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=4,
                learning_rate=0.1,
                random_state=42
            )
            model.fit(X_train, y_train)

            # Evaluate
            y_pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))

            # Check if we should use this model
            active_model = ModelVersion.query.filter_by(status='active').first()
            if active_model:
                old_metrics = active_model.get_metrics()
                old_mae = old_metrics.get('mae', float('inf'))
                if mae > old_mae * 1.5:  # New model is significantly worse
                    # Keep old model, mark new as failed
                    version_num = f"v{active_model.id + 1}.0"
                    failed_version = ModelVersion(
                        version_number=version_num,
                        training_data_count=len(df),
                        status='failed',
                        notes=f'MAE {mae:.4f} was worse than current {old_mae:.4f}'
                    )
                    failed_version.set_metrics({'mae': round(mae, 4), 'rmse': round(rmse, 4)})
                    db.session.add(failed_version)
                    db.session.commit()
                    return {
                        'success': False,
                        'error': f'New model worse than current (MAE: {mae:.4f} vs {old_mae:.4f}). Keeping existing model.',
                        'method': 'ml-rejected'
                    }

            # Save model to disk
            next_id = (active_model.id + 1) if active_model else 1
            version_num = f"v{next_id}.0"
            model_path = os.path.join(self.model_dir, f"demand_model_{version_num}.joblib")
            joblib.dump(model, model_path)

            # Retire old active model
            if active_model:
                active_model.status = 'retired'

            # Create new model version record
            new_version = ModelVersion(
                version_number=version_num,
                training_data_count=len(df),
                status='active',
                model_file_path=model_path,
                notes=f'Trained on {len(df)} booking records'
            )
            new_version.set_metrics({'mae': round(mae, 4), 'rmse': round(rmse, 4)})
            db.session.add(new_version)
            db.session.commit()

            # Update in-memory model
            self.model = model

            # Generate predictions for next 7 days
            self._generate_ml_predictions(model, new_version.id)

            return {
                'success': True,
                'message': f'Model {version_num} trained successfully. MAE: {mae:.4f}, RMSE: {rmse:.4f}',
                'method': 'ml',
                'metrics': {'mae': round(mae, 4), 'rmse': round(rmse, 4)},
                'version': version_num,
                'data_points': len(df)
            }

        except Exception as e:
            traceback.print_exc()
            return {'success': False, 'error': str(e)}

    def _generate_ml_predictions(self, model, model_version_id):
        """Generate predictions for the next 7 days using trained model."""
        from app.models import db
        from app.models.prediction import DemandPrediction
        from app.models.setting import Setting

        open_hour = int(Setting.get('open_hour', '8'))
        close_hour = int(Setting.get('close_hour', '22'))

        # Delete old predictions for future dates
        today = date.today()
        DemandPrediction.query.filter(DemandPrediction.date >= today).delete()

        for day_offset in range(7):
            pred_date = today + timedelta(days=day_offset)
            for hour in range(open_hour, close_hour):
                features = np.array([[
                    hour,
                    pred_date.weekday(),
                    1 if pred_date.weekday() >= 5 else 0,
                    pred_date.month,
                    pred_date.isocalendar()[1]
                ]])

                predicted_occ = float(np.clip(model.predict(features)[0], 0, 1))

                # Determine label
                if predicted_occ >= 0.7:
                    label = 'busy'
                elif predicted_occ >= 0.4:
                    label = 'moderate'
                else:
                    label = 'quiet'

                capacity = int(Setting.get('total_capacity', '30'))
                predicted_bookings = int(predicted_occ * capacity)

                prediction = DemandPrediction(
                    date=pred_date,
                    time_slot=f"{hour:02d}:00-{hour+1:02d}:00",
                    predicted_occupancy=round(predicted_occ, 3),
                    predicted_bookings=predicted_bookings,
                    predicted_label=label,
                    model_version_id=model_version_id
                )
                db.session.add(prediction)

        db.session.commit()

    def _generate_rule_based_predictions(self):
        """Generate simple rule-based predictions when not enough data."""
        from app.models import db
        from app.models.prediction import DemandPrediction
        from app.models.setting import Setting

        open_hour = int(Setting.get('open_hour', '8'))
        close_hour = int(Setting.get('close_hour', '22'))

        today = date.today()
        DemandPrediction.query.filter(DemandPrediction.date >= today).delete()

        # Simple heuristic: busier during lunch (12-14) and evening (17-20), weekends slightly busier
        for day_offset in range(7):
            pred_date = today + timedelta(days=day_offset)
            is_weekend = pred_date.weekday() >= 5

            for hour in range(open_hour, close_hour):
                base = 0.2
                if 12 <= hour <= 14:
                    base = 0.55  # Lunch rush
                elif 17 <= hour <= 20:
                    base = 0.5  # Evening rush
                elif 9 <= hour <= 11:
                    base = 0.35  # Morning coffee
                elif hour >= 21:
                    base = 0.15  # Late evening

                if is_weekend:
                    base = min(base * 1.3, 0.95)

                # Add some variance
                import random
                variance = random.uniform(-0.05, 0.05)
                occupancy = max(0, min(1, base + variance))

                if occupancy >= 0.7:
                    label = 'busy'
                elif occupancy >= 0.4:
                    label = 'moderate'
                else:
                    label = 'quiet'

                capacity = int(Setting.get('total_capacity', '30'))

                prediction = DemandPrediction(
                    date=pred_date,
                    time_slot=f"{hour:02d}:00-{hour+1:02d}:00",
                    predicted_occupancy=round(occupancy, 3),
                    predicted_bookings=int(occupancy * capacity),
                    predicted_label=label,
                    model_version_id=None
                )
                db.session.add(prediction)

        db.session.commit()

    def predict_slot(self, target_date, hour):
        """Get prediction for a specific date and time slot."""
        from app.models.prediction import DemandPrediction

        slot = f"{hour:02d}:00-{hour+1:02d}:00"
        prediction = DemandPrediction.query.filter_by(
            date=target_date, time_slot=slot
        ).first()

        if prediction:
            return prediction.to_dict()

        return {
            'predicted_occupancy': 0.3,
            'predicted_label': 'moderate',
            'predicted_bookings': 0,
            'model_version': 'none'
        }

    def get_weekly_predictions(self):
        """Get predictions for the next 7 days."""
        from app.models.prediction import DemandPrediction

        today = date.today()
        end_date = today + timedelta(days=7)

        predictions = DemandPrediction.query.filter(
            DemandPrediction.date >= today,
            DemandPrediction.date < end_date
        ).order_by(DemandPrediction.date, DemandPrediction.time_slot).all()

        return [p.to_dict() for p in predictions]


# Singleton
demand_predictor = DemandPredictor()

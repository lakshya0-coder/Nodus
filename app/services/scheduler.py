"""
APScheduler-based scheduler for weekly ML model retraining.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


scheduler = BackgroundScheduler()
_app = None


def init_scheduler(app):
    """Initialize the scheduler with the Flask app."""
    global _app
    _app = app

    # Weekly retraining job — every Sunday at midnight
    scheduler.add_job(
        func=_retrain_job,
        trigger=CronTrigger(day_of_week='sun', hour=0, minute=0),
        id='weekly_ml_retrain',
        name='Weekly ML Demand Model Retraining',
        replace_existing=True
    )

    # Daily prediction refresh — every day at 1 AM
    scheduler.add_job(
        func=_refresh_predictions_job,
        trigger=CronTrigger(hour=1, minute=0),
        id='daily_prediction_refresh',
        name='Daily Prediction Refresh',
        replace_existing=True
    )

    if not scheduler.running:
        scheduler.start()

    print("[Scheduler] Started — Weekly retraining: Sunday 00:00, Daily refresh: 01:00")


def _retrain_job():
    """Execute the ML retraining pipeline."""
    global _app
    if _app is None:
        return

    with _app.app_context():
        from app.services.ml_predictor import demand_predictor
        print("[Scheduler] Starting weekly ML retraining...")
        result = demand_predictor.train()
        print(f"[Scheduler] Retraining complete: {result}")


def _refresh_predictions_job():
    """Refresh predictions daily using the current model."""
    global _app
    if _app is None:
        return

    with _app.app_context():
        from app.services.ml_predictor import demand_predictor
        from app.models.prediction import ModelVersion
        import joblib

        active = ModelVersion.query.filter_by(status='active').first()
        if active and active.model_file_path:
            import os
            if os.path.exists(active.model_file_path):
                model = joblib.load(active.model_file_path)
                demand_predictor._generate_ml_predictions(model, active.id)
                print("[Scheduler] Daily predictions refreshed with active ML model.")
                return

        # Fallback to rule-based
        demand_predictor._generate_rule_based_predictions()
        print("[Scheduler] Daily predictions refreshed with rule-based estimates.")


def trigger_retrain():
    """Manually trigger a retraining job."""
    _retrain_job()


def get_scheduler_status():
    """Get current scheduler status."""
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            'id': job.id,
            'name': job.name,
            'next_run': str(job.next_run_time) if job.next_run_time else 'N/A',
            'trigger': str(job.trigger)
        })
    return {
        'running': scheduler.running,
        'jobs': jobs
    }

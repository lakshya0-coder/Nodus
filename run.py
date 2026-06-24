"""
Nodus Cafe — Application Entry Point
Run: python run.py
"""
import os
from dotenv import load_dotenv
load_dotenv()
from app import create_app
from app.services.ai_assistant import ai_assistant
from app.services.ml_predictor import demand_predictor
from app.services.scheduler import init_scheduler

app = create_app()

# Initialize services
with app.app_context():
    ai_assistant.init_app(app)
    demand_predictor.init_app(app)

# Start scheduler
init_scheduler(app)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"""
╔══════════════════════════════════════════════╗
║           ☕ NODUS CAFE SERVER ☕             ║
╠══════════════════════════════════════════════╣
║  Running at: http://localhost:{port}           ║
║  Admin Panel: http://localhost:{port}/admin     ║
║  Login: admin / admin123                     ║
╠══════════════════════════════════════════════╣
║  Press Ctrl+C to stop                        ║
╚══════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)

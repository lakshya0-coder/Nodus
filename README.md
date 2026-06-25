# Nodus Cafe

**A modern cafe website with AI drink recommendations, smart booking, admin management, ML demand prediction, and bilingual (EN/HI) support.**

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Seed the database with demo data
python seed_data.py

# 3. Run the application
python run.py
```

The app will be available at **http://localhost:5000**

## Features

### Public Website
- **Home** — Hero section, featured drinks, AI teaser, testimonials
- **Menu** — Categorized menu with search & filters, bilingual (EN/HI)
- **Slot Booking** — Calendar-based booking with demand predictions
- **About** — Brand story, values, gallery
- **Contact** — Address, hours, contact form

### AI Chat Assistant
- Gemini-powered drink recommendations
- Menu-grounded (only suggests real items)
- Bilingual (English + Hindi)
- Full conversation logging
- Keyword-based fallback when API unavailable

### Admin Panel (`/admin`)
- **Dashboard** — Today's stats, charts, quick actions
- **Orders** — Status management (received → preparing → ready → completed)
- **Bookings** — Calendar + list view, manual booking
- **Menu Management** — CRUD for categories and items with EN/HI translations
- **Demand Forecast** — ML predictions heatmap, model version history
- **AI Conversations** — Searchable logs with feedback analytics
- **Staff Management** — User roles and permissions
- **Settings** — Cafe hours, capacity, API keys

### ML Demand Predictor
- Gradient Boosting model trained on booking history
- Weekly automatic retraining (Sunday midnight)
- Model versioning with rollback
- Rule-based cold-start fallback
- Predictions integrated into booking page

### Multi-language
- English and Hindi across all pages
- Language toggle in header, persisted in cookie
- Menu items have managed translations
- AI responds in user's preferred language

## Tech Stack

- **Backend**: Python Flask, SQLite
- **Frontend**: Vanilla HTML/CSS/JS, Jinja2
- **AI**: Google Gemini API
- **ML**: scikit-learn (Gradient Boosting)
- **Scheduler**: APScheduler
- **Fonts**: Playfair Display, Inter, Noto Sans Devanagari

## Project Structure

```
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration
│   ├── models/              # SQLAlchemy models
│   ├── routes/              # Flask blueprints & API
│   ├── services/            # AI, ML, i18n services
│   ├── static/              # CSS, JS, images
│   ├── templates/           # Jinja2 HTML templates
│   └── translations/        # EN/HI JSON files
├── ml/
│   └── models/              # Saved ML models
├── instance/
│   └── nodus_cafe.db        # SQLite database
├── seed_data.py             # Demo data seeder
├── run.py                   # Entry point
└── requirements.txt         # Dependencies
```

## AI Setup (Optional)

To enable the AI chat assistant, set your Gemini API key:
1. Go to Admin → Settings
2. Enter your Google Gemini API key
3. The AI assistant will activate immediately

Without an API key, the assistant uses keyword-based recommendations.

## License

Private project for Nodus Cafe.

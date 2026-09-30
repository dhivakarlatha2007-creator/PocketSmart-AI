# PocketSmart AI — Your Smart Budget & Recommendation Assistant

A beginner-friendly personal finance web app built with Python Flask, SQLite, HTML, and CSS. It records income and expenses, summarizes the wallet, tracks a monthly budget, and produces explainable rule-based recommendations.

## Features
- Add income and expense transactions with category, note, and date
- Dashboard showing total income, expenses, balance, and monthly budget
- Recent transaction history and delete option
- Set a monthly budget
- Rule-based recommendations based on recorded spending
- SQLite database is created automatically

> “AI recommendations” in this student project are transparent rule-based insights, not a trained machine-learning model or a financial adviser.

## Run locally
1. Install Python 3.10 or later.
2. Open a terminal in this folder.
3. Create and activate a virtual environment (optional but recommended):
   - Windows: `python -m venv .venv` then `.venv\\Scripts\\activate`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Start the app: `python app.py`
6. Open `http://127.0.0.1:5000` in your browser.

The database `pocketsmart.db` will be created in the project folder. Use only sample data for classroom demonstrations; this prototype has no login or production security controls.

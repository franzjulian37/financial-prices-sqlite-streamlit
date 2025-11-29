# Small Finance DB + Streamlit Dashboard

A small project which downloads prices with `yfinance`, saves a SQLite DB, compute basic matrics and shows as output a Streamlit dashboard.

This project aims at showing a simple yet functioning data pipeline for financial applications. My humble opinion is that this is more relevant than a single colab notebook full of high-level financial math - something that nowadays AI can easily write for yourself - while real work is more about creating and maintaining complete systems, from data collection to visualization.

## Rep structure
- `load_prices_yf.py` — download prices and sets `db/prices_yf.db`
- `compute_metrics_yf.py` — reads DB, compute metrics and produces `data/METRICS_YF.csv`
- `streamlit_app_yf.py` — app Streamlit which reads `data/METRICS_YF.csv` and generate dashboard
- `db/` — SQLite DB folder (prices_yf.db)
- `data/` — output CSV folder (METRICS_YF.csv)

## Esecuzione locale (quickstart)
1. Create and activates virtualenv (see requirements.txt for details):
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # macOS / Linux
   .venv\Scripts\activate      # Windows

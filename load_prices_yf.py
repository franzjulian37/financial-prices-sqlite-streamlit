import sqlite3
from datetime import datetime
import yfinance as yf
import pandas as pd
import os
from pathlib import Path

DB_PATH = os.path.join(os.path.dirname(__file__), "db", "prices_yf.db")

TICKERS = ["AAPL", "MSFT", "GOOG"]

#repo_root = Path(__file__).parent.parent
#data_raw = repo_root / "data" / "raw"
#data_raw.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# CREA TABELLA SE NON ESISTE
# -----------------------------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            ticker TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            PRIMARY KEY (ticker, date)
        );
    """)

    conn.commit()
    conn.close()

# -----------------------------------------------------------------------------
# SCARICA E NORMALIZZA I DATI
# -----------------------------------------------------------------------------
def download_prices(ticker: str) -> pd.DataFrame:
    print(f"Scaricando {ticker}...")

    df = yf.download(
        ticker,
        start="2023-01-01",
        end="2025-01-01",
        auto_adjust=True
    )

    # Se vuoto → ritorna direttamente
    if df.empty:
        print(f"Nessun dato per {ticker}")
        return pd.DataFrame()

    df = df.reset_index()

    # Normalizza colonne
    df.rename(columns={
        "Date": "date",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume"
    }, inplace=True)

    # Ticker come colonna scalare
    df["ticker"] = ticker

    # Assicurati che date sia string YYYY-MM-DD
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    # Mantieni solo le colonne necessarie
    cols = ["ticker", "date", "open", "high", "low", "close", "volume"]

    return df[cols]

# -----------------------------------------------------------------------------
# INSERIMENTO ROBUSTO (TUPLE SCALARI)
# -----------------------------------------------------------------------------
def insert_into_db(df: pd.DataFrame):
    if df.empty:
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    rows = list(df.itertuples(index=False, name=None))

    cur.executemany("""
        INSERT OR REPLACE INTO prices 
        (ticker, date, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, rows)

    conn.commit()
    conn.close()

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    init_db()

    all_data = []

    for ticker in TICKERS:
        df = download_prices(ticker)
        insert_into_db(df)

    print("\n✓ Completato senza errori.")



# scripts/export_csv_from_db.py

# --- Percorso DB e cartella CSV ---
repo_root = Path(__file__).parent
db_path = repo_root / "db" / "prices_yf.db"
data_csv = repo_root / "data"
data_csv.mkdir(parents=True, exist_ok=True)

# --- Connessione DB ---
conn = sqlite3.connect(db_path)

# --- Trova tutti i ticker disponibili ---
tickers = pd.read_sql("SELECT DISTINCT ticker FROM prices", conn)
tickers_list = tickers['ticker'].tolist()

for ticker in tickers_list:
    print(f"Esportando CSV per {ticker}...")
    
    # Leggi dati del ticker ordinati per data
    df = pd.read_sql(f"""
        SELECT ticker, date, open, high, low, close, volume
        FROM prices
        WHERE ticker = '{ticker}'
        ORDER BY date
    """, conn)
    
    # Salva CSV
    csv_file = data_csv / f"{ticker}.csv"
    df.to_csv(csv_file, index=False)
    print(f"Salvato {csv_file} ({len(df)} righe)")

conn.close()
print("✓ Tutti i CSV esportati dal DB.")

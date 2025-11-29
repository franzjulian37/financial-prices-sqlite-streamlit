# scripts/compute_metrics.py
import pandas as pd
import sqlite3
from pathlib import Path
import numpy as np

repo_root = Path.cwd()
db_path = repo_root / "db" / "prices_yf.db"
output_csv = repo_root / "data" / "METRICS_YF.csv"
output_csv.parent.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(db_path)

# Leggi tutti i dati dal DB
df = pd.read_sql("SELECT * FROM prices", conn, parse_dates=["date"])
conn.close()

# --- Data cleaning checks ----------------------------------------------------

# Controllo colonne attese
expected_cols = {"date", "ticker", "close"}
missing_cols = expected_cols - set(df.columns)
if missing_cols:
    raise ValueError(f"Missing expected columns in dataset: {missing_cols}")

# Droppa righe completamente vuote (rarissimo ma buono da fare)
df.dropna(how="all", inplace=True)

# Rimuove righe con NA nelle colonne critiche
df.dropna(subset=["date", "ticker", "close"], inplace=True)

# Converti date se non già convertite (robustezza)
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df.dropna(subset=["date"], inplace=True)

# Ordina i dati per sicurezza
df.sort_values(by=["ticker", "date"], inplace=True)

# Reset index pulito
df.reset_index(drop=True, inplace=True)

metrics_list = []


for ticker in df["ticker"].unique():
    df_t = df[df["ticker"] == ticker].sort_values("date").copy()
    
    # Rendimenti logaritmici
    df_t["log_return"] = np.log(df_t["close"] / df_t["close"].shift(1))
    
    # Volatilità rolling 30 giorni
    df_t["vol_30d"] = df_t["log_return"].rolling(window=30).std()
    
    # VaR parametrico al 95%
    df_t["VaR_95"] = df_t["log_return"].mean() - 1.65 * df_t["log_return"].std()
    
    metrics_list.append(df_t)

# Unisci tutto
metrics_df = pd.concat(metrics_list)
metrics_df.to_csv(output_csv, index=False)

print(f"Metriche calcolate e salvate in {output_csv} ✅")

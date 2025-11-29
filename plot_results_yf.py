# scripts/plot_results.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

repo_root = Path.cwd()
metrics_csv = repo_root / "data"  / "METRICS_YF.csv"

df = pd.read_csv(metrics_csv, parse_dates=["date"])

sns.set(style="whitegrid")

for ticker in df["ticker"].unique():
    df_t = df[df["ticker"] == ticker]
    
    plt.figure(figsize=(10,5))
    plt.plot(df_t["date"], df_t["close"], label="Close Price")
    plt.title(f"{ticker} - Prezzo Storico")
    plt.xlabel("Date")
    plt.ylabel("Close")
    plt.legend()
    plt.tight_layout()
    plt.show()
    
    plt.figure(figsize=(10,5))
    plt.plot(df_t["date"], df_t["vol_30d"], label="Volatilità 30 giorni", color="orange")
    plt.title(f"{ticker} - Volatilità Rolling 30 giorni")
    plt.xlabel("Date")
    plt.ylabel("Volatilità")
    plt.legend()
    plt.tight_layout()
    plt.show()

# streamlit_app.py
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

CURRENT_DIR = Path.cwd()

# Prende il CSV generato da compute_metrics_yf.py
METRICS_CSV = CURRENT_DIR / "data" / "METRICS_YF.csv"

# Leggi il CSV
df = pd.read_csv(METRICS_CSV)
st.set_page_config(page_title="Stock Metrics", layout="wide")

# --- Utility: lettura dati con cache ---
@st.cache_data(ttl=3600)
def load_metrics(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        return pd.DataFrame()  # vuoto se manca
    df = pd.read_csv(csv_path, parse_dates=["date"])
    # Assicurati colonne previste (close, vol_30d, ticker, date)
    return df

df = load_metrics(METRICS_CSV)

# --- Header ---
st.title("📈 Stock metrics dashboard")
st.markdown("Shows data computed by script. Use sidebar to choose ticker and interval.")

# --- Sidebar: filtri ---
with st.sidebar:
    st.header("Filtri")
    if df.empty:
        st.warning("File csv not found. Execute `compute_metrics_yf.py` before running Streamlit.")
    else:
        tickers = sorted(df["ticker"].unique())
        selectors = st.multiselect("Choose ticker", options=tickers, default=tickers[:2] if tickers else [])
        min_date = df["date"].min().date()
        max_date = df["date"].max().date()
        date_range = st.date_input("Dates interval", value=(min_date, max_date), min_value=min_date, max_value=max_date)
        show_table = st.checkbox("Show data table", value=False)

# --- Main: filtra dati ---
if not df.empty and selectors:
    start_date, end_date = date_range
    mask = df["ticker"].isin(selectors) & (df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)
    df_f = df.loc[mask].copy()

    if df_f.empty:
        st.info("No data for the selected filter.")
    else:
        # Grafico 1: Prezzo storico (interattivo)
        st.subheader("Closing price")
        fig_price = px.line(
            df_f,
            x="date",
            y="close",
            color="ticker",
            title="Close Price per ticker",
            labels={"close": "Close", "date": "Date"}
        )
        fig_price.update_layout(height=400, margin=dict(l=20,r=20,t=40,b=20))
        st.plotly_chart(fig_price, use_container_width=True)

        # Grafico 2: Volatilità rolling 30d
        st.subheader("30-days rolling volatility")
        fig_vol = px.line(
            df_f,
            x="date",
            y="vol_30d",
            color="ticker",
            title="volatility (30d rolling)",
            labels={"vol_30d": "Volatilità"}
        )
        fig_vol.update_layout(height=380, margin=dict(l=20,r=20,t=40,b=20))
        st.plotly_chart(fig_vol, use_container_width=True)

        # Tabelle / statistiche aggregate
        st.subheader("Metrics")
        summary = df_f.groupby("ticker").agg(
            first_date=("date", "min"),
            last_date=("date", "max"),
            mean_return=("log_return", "mean"),
            std_return=("log_return", "std"),
            mean_vol30=("vol_30d", "mean")
        ).reset_index()
        # formatta date
        summary["first_date"] = pd.to_datetime(summary["first_date"]).dt.date
        summary["last_date"] = pd.to_datetime(summary["last_date"]).dt.date

        st.dataframe(summary)

        if show_table:
            st.subheader("Filtered raw data")
            st.dataframe(df_f.sort_values(["ticker", "date"]).reset_index(drop=True))

        # Download CSV del sottoinsieme
        csv_bytes = df_f.to_csv(index=False).encode("utf-8")
        st.download_button("Download filtered csv", data=csv_bytes, file_name="metrics_filtered.csv", mime="text/csv")

else:
    if df.empty:
        st.info("metrics.csv not found or empty.")
    else:
        st.info("Select at least a ticker in the sidebar.")

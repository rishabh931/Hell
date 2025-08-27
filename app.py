import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import google.generativeai as genai

# -------------------------------
# Sidebar: Gemini API Key
# -------------------------------
st.sidebar.header("🔑 API Configuration")
gemini_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if gemini_key:
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
else:
    model = None
    st.warning("⚠️ Please enter your Gemini API key in the sidebar to enable AI analysis.")

# -------------------------------
# User Input
# -------------------------------
st.title("📊 Indian Stock Quarterly Results with AI Insights (Yahoo Finance)")

stock_symbol = st.text_input(
    "Enter NSE Stock Symbol (e.g. RELIANCE.NS, TCS.NS, HDFCBANK.NS):",
    help="Use Yahoo Finance format (append .NS for NSE stocks)"
)

# -------------------------------
# Function to fetch data from Yahoo Finance
# -------------------------------
def get_yahoo_financials(symbol: str):
    ticker = yf.Ticker(symbol)

    # Quarterly financials
    fin = ticker.quarterly_financials.T
    fin = fin.reset_index().rename(columns={"index": "Quarter"})

    # Quarterly earnings (EPS, revenue)
    earn = ticker.quarterly_earnings.reset_index()

    # Merge earnings with financials
    df = pd.merge(fin, earn, left_on="Quarter", right_on="Quarter", how="outer")

    # Keep only last 10 quarters
    df = df.tail(10)

    # Rename columns
    rename_map = {
        "Total Revenue": "Sales",
        "Operating Income": "Operating Profit",
        "Net Income": "Net Profit",
        "Earnings": "EPS",
        "Revenue": "Sales (Earnings Tab)"
    }
    df = df.rename(columns=rename_map)

    # Calculate OPM%
    if "Operating Profit" in df.columns and "Sales" in df.columns:
        df["OPM%"] = (df["Operating Profit"] / df["Sales"]) * 100

    return df

# -------------------------------
# Main Logic
# -------------------------------
if stock_symbol:
    try:
        df = get_yahoo_financials(stock_symbol)

        if not df.empty:
            st.subheader(f"📑 Consolidated Quarterly Results - {stock_symbol}")
            st.dataframe(df)

            # Plot charts
            for col in ["Sales", "Operating Profit", "OPM%", "Net Profit", "EPS"]:
                if col in df.columns:
                    fig, ax = plt.subplots()
                    ax.plot(df["Quarter"], df[col], marker="o")
                    ax.set_title(f"{col} Trend")
                    ax.set_xticklabels(df["Quarter"], rotation=45, ha="right")
                    st.pyplot(fig)

            # Gemini AI Analysis
            if model:
                prompt = f"""
                Analyze the last 10 consolidated quarters of {stock_symbol} based on this dataset:
                {df.to_string(index=False)}
                
                Provide insights for:
                - Sales growth
                - Operating Profit trends
                - OPM% margins
                - Net Profit performance
                - EPS movement
                
                Highlight positives & negatives in simple words.
                """
                with st.spinner("🤖 Gemini is analyzing data..."):
                    response = model.generate_content(prompt)
                    st.subheader("🔎 Gemini AI Insights")
                    st.write(response.text)
        else:
            st.error("No data found for this symbol on Yahoo Finance.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")

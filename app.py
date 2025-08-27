import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
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
st.title("📊 Indian Stock Quarterly Results with AI Insights")

stock_symbol = st.text_input("Enter NSE Stock Symbol (e.g. RELIANCE, TCS, HDFCBANK):")

# -------------------------------
# Function to fetch NSE results (Consolidated only)
# -------------------------------
def get_nse_results(symbol: str):
    url = f"https://www.nseindia.com/api/results-comparison?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://www.nseindia.com/",
    }
    session = requests.Session()
    resp = session.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return data.get("consolidated", [])

# -------------------------------
# Main Logic
# -------------------------------
if stock_symbol:
    try:
        results = get_nse_results(stock_symbol)
        if results:
            df = pd.DataFrame(results)
            df = df.tail(10)   # last 10 quarters

            # Rename important cols if they exist
            rename_map = {
                "quarter": "Quarter",
                "totalIncome": "Sales",
                "pbdt": "Operating Profit",
                "opm": "OPM%",
                "netProfit": "Net Profit",
                "eps": "EPS"
            }
            df = df.rename(columns=rename_map)

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
                
                Give detailed insights separately for:
                - Sales growth
                - Operating Profit trends
                - OPM% margins
                - Net Profit performance
                - EPS movement
                
                Provide easy-to-understand commentary with positive/negative highlights.
                """
                with st.spinner("🤖 Gemini is analyzing data..."):
                    response = model.generate_content(prompt)
                    st.subheader("🔎 Gemini AI Insights")
                    st.write(response.text)
        else:
            st.error("No consolidated results found for this symbol.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")

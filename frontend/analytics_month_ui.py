import streamlit as st
from datetime import datetime
import requests
import pandas as pd

API_URL = "http://localhost:8000"

def analytics_month_tab():

    if st.button("Get Month Analytics"):
        response = requests.get(f"{API_URL}/month")
        monthly_summary = response.json()

        df = pd.DataFrame(monthly_summary)
        df.rename(columns= {
            "expense_month": "Month Number",
            "month_name": "Month Name",
            "total_amount": "Total"
        }, inplace=True)
        df_sorted = df.sort_values(by="Month Number", ascending=True)
        df_sorted.set_index('Month Number',inplace=True)

        st.title("Expense Breakdown By Months")

        st.bar_chart(df_sorted, x="Month Name", color="#FF6500")

        st.table(df_sorted)





import streamlit as st
import pandas as pd

def show_most_features(df):
    st.header("Most Features Asked by Merchant")
    features_list = [
        "Appointment", "Attendance", "Classroom", "E-Invoice", "Expenses", "General", "HARDWARE", "History", "Inventory", "Mall Integration", "Member", "Menu", "Message", "Online", "Booking", "Order", "Queue", "Receipt", "Report", "Roster", "Settings", "Shift", "Report", "SQL Integration", "Staff", "Tunai App", "Tunai Biz", "Tunai Staff", "Voucher", "Walk-in"
    ]
    feature_counts = df['Features Category'].value_counts().reset_index()
    feature_counts.columns = ['Feature', 'Count']
    feature_counts = feature_counts[feature_counts['Feature'].isin(features_list)]
    st.bar_chart(feature_counts.set_index('Feature'))
    st.write("---")
    st.subheader("Feature Requests by Merchant")
    pivot = pd.pivot_table(df, index='Merchants', columns='Features Category', aggfunc='size', fill_value=0)
    st.dataframe(pivot)

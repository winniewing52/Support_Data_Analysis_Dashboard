import streamlit as st
import pandas as pd
import plotly.express as px

def show_most_features(df):
    st.header("Most Features Asked by Merchant")
    
    # Add sorting option
    sort_option = st.selectbox(
        "Sort by:",
        ["Default", "Highest to Lowest", "Lowest to Highest"]
    )
    
    features_list = [
        "Appointment", "Attendance", "Classroom", "E-Invoice", "Expenses", "General", "HARDWARE", "History", "Inventory", "Mall Integration", "Member", "Menu", "Message", "Online", "Booking", "Order", "Queue", "Receipt", "Report", "Roster", "Settings", "Shift", "Report", "SQL Integration", "Staff", "Tunai App", "Tunai Biz", "Tunai Staff", "Voucher", "Walk-in"
    ]
    feature_counts = df['Features Category'].value_counts().reset_index()
    feature_counts.columns = ['Feature', 'Count']
    feature_counts = feature_counts[feature_counts['Feature'].isin(features_list)]
    
    # Apply sorting based on selected option
    if sort_option == "Default":
        feature_counts = feature_counts.sort_values('Feature')
    elif sort_option == "Highest to Lowest":
        feature_counts = feature_counts.sort_values('Count', ascending=False)
    elif sort_option == "Lowest to Highest":
        feature_counts = feature_counts.sort_values('Count', ascending=True)
    
    # Create bar chart with plotly to preserve sorting order
    fig = px.bar(feature_counts, x='Feature', y='Count', 
                 title='Feature Requests Count',
                 labels={'Feature': 'Feature', 'Count': 'Count'})
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    st.write("---")
    st.subheader("Feature Requests by Merchant")
    pivot = pd.pivot_table(df, index='Merchants', columns='Features Category', aggfunc='size', fill_value=0)
    st.dataframe(pivot)

import streamlit as st

def show_total_questions(df):
    st.header("Total Questions & Merchants")
    total_questions = len(df)
    total_merchants = df['Merchants'].nunique()
    st.metric("Total Questions Asked", total_questions)
    st.metric("Total Merchants", total_merchants)
    st.write("---")
    st.subheader("Questions by Merchant")
    merchant_counts = df['Merchants'].value_counts().reset_index()
    merchant_counts.columns = ['Merchant', 'Questions Asked']
    # Display with 1-based row index
    merchant_counts.index = merchant_counts.index + 1
    st.dataframe(merchant_counts)

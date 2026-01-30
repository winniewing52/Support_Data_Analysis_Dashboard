import streamlit as st
import pandas as pd

def show_top_sales_curiosity(df):
    df.columns = df.columns.str.strip()
    st.header("Top Sales with Most Customer's Curiosity")
    sales_list = ["Danny", "Dylan", "Erica", "Hazwan", "Jun", "Kyle", "Old Sales", "Qis", "Raymond", "Tammy", "Tom"]
    sales_counts = df['Sales'].value_counts().reset_index()
    sales_counts.columns = ['Sales', 'Questions Asked']
    sales_counts = sales_counts[sales_counts['Sales'].isin(sales_list)]
    st.bar_chart(sales_counts.set_index('Sales'))
    st.write("---")
    st.subheader("Questions by Sales")
    # Display with 1-based row index
    sales_counts.index = sales_counts.index + 1
    st.dataframe(sales_counts)

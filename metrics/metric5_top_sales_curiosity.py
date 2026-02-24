import streamlit as st
import pandas as pd
import plotly.express as px

def show_top_sales_curiosity(df, key_suffix=""):
    df.columns = df.columns.str.strip()
    st.header("Top Sales with Most Customer's Curiosity")
    
    # Add sorting option
    sort_option = st.selectbox(
        "Sort by:",
        ["Default", "Highest to Lowest", "Lowest to Highest"],
        key=f"sort_metric5{key_suffix}"
    )
    
    sales_list = ["Danny", "Dylan", "Erica", "Hazwan", "Jun", "Kyle", "Old Sales", "Qis", "Raymond", "Tammy", "Tom"]
    sales_counts = df['Sales'].value_counts().reset_index()
    sales_counts.columns = ['Sales', 'Questions Asked']
    sales_counts = sales_counts[sales_counts['Sales'].isin(sales_list)]
    
    # Apply sorting based on selected option
    if sort_option == "Default":
        sales_counts = sales_counts.sort_values('Sales')
    elif sort_option == "Highest to Lowest":
        sales_counts = sales_counts.sort_values('Questions Asked', ascending=False)
    elif sort_option == "Lowest to Highest":
        sales_counts = sales_counts.sort_values('Questions Asked', ascending=True)
    
    # Create bar chart with plotly to preserve sorting order
    fig = px.bar(sales_counts, x='Sales', y='Questions Asked', 
                 title='Questions Asked by Sales',
                 labels={'Sales': 'Sales Person', 'Questions Asked': 'Questions Asked'})
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    st.write("---")
    st.subheader("Questions by Sales")
    # Display with 1-based row index
    sales_counts.index = sales_counts.index + 1
    st.dataframe(sales_counts)

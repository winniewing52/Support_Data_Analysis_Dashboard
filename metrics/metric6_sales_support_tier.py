import streamlit as st
import pandas as pd
import plotly.express as px

def show_sales_support_tier(df):
    df.columns = df.columns.str.strip()
    st.header("IT Support Tier for Each Sales")
    
    # Prepare data for interactive chart
    sales_tier = df.groupby(['Sales', 'IT Support Tier']).size().reset_index(name='Count')
    
    st.subheader("Interactive Chart: IT Support Tier by Sales")
    st.write("*Click on the legend items to show/hide specific support tiers*")
    
    # Create interactive stacked bar chart
    fig = px.bar(sales_tier, 
                 x='Sales', 
                 y='Count',
                 color='IT Support Tier',
                 title='IT Support Tier Distribution by Sales Person',
                 labels={'Count': 'Number of Questions', 'Sales': 'Sales Person'},
                 barmode='stack')
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=600,
        legend_title_text='IT Support Tier (Click to toggle)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.write("---")
    
    st.subheader("Sales & IT Support Tier Details")
    
    # Add filters for the table
    col1, col2 = st.columns(2)
    with col1:
        sales_options = ['All'] + sorted(sales_tier['Sales'].unique().tolist())
        selected_sales = st.selectbox('Filter by Sales:', sales_options, key='filter_sales_tier_table')
    with col2:
        tier_options = ['All'] + sorted(sales_tier['IT Support Tier'].unique().tolist())
        selected_tier = st.selectbox('Filter by IT Support Tier:', tier_options, key='filter_tier_sales_table')
    
    # Apply filters
    filtered_sales_tier = sales_tier.copy()
    if selected_sales != 'All':
        filtered_sales_tier = filtered_sales_tier[filtered_sales_tier['Sales'] == selected_sales]
    if selected_tier != 'All':
        filtered_sales_tier = filtered_sales_tier[filtered_sales_tier['IT Support Tier'] == selected_tier]
    
    table_data = filtered_sales_tier.sort_values('Count', ascending=False).reset_index(drop=True)
    table_data.index = table_data.index + 1
    st.dataframe(table_data)
    
    st.write("---")
    
    pivot = pd.pivot_table(df, index='Sales', columns='IT Support Tier', aggfunc='size', fill_value=0)
    st.dataframe(pivot)
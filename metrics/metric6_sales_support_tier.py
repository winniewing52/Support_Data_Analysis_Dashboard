import streamlit as st
import pandas as pd
import plotly.express as px

def show_sales_support_tier(df, key_suffix=""):
    df.columns = df.columns.str.strip()
    st.header("IT Support Tier for Each Sales")
    
    # Add sorting option
    sort_option = st.selectbox(
        "Sort by:",
        ["Default", "Highest to Lowest", "Lowest to Highest"],
        key=f"sort_metric6{key_suffix}"
    )
    
    # Prepare data for interactive chart
    sales_tier = df.groupby(['Sales', 'IT Support Tier']).size().reset_index(name='Count')
    
    # Calculate total count per sales person for sorting
    sales_totals = sales_tier.groupby('Sales')['Count'].sum().reset_index()
    sales_totals.columns = ['Sales', 'Total']
    
    # Apply sorting based on selected option
    if sort_option == "Default":
        sales_totals = sales_totals.sort_values('Sales')
    elif sort_option == "Highest to Lowest":
        sales_totals = sales_totals.sort_values('Total', ascending=False)
    elif sort_option == "Lowest to Highest":
        sales_totals = sales_totals.sort_values('Total', ascending=True)
    
    # Reorder sales_tier based on sorted sales_totals
    sales_tier['Sales'] = pd.Categorical(
        sales_tier['Sales'],
        categories=sales_totals['Sales'].tolist(),
        ordered=True
    )
    sales_tier = sales_tier.sort_values('Sales')
    
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
        selected_sales = st.selectbox('Filter by Sales:', sales_options, key=f'filter_sales_tier_table{key_suffix}')
    with col2:
        tier_options = ['All'] + sorted(sales_tier['IT Support Tier'].unique().tolist())
        selected_tier = st.selectbox('Filter by IT Support Tier:', tier_options, key=f'filter_tier_sales_table{key_suffix}')
    
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
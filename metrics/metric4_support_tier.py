import streamlit as st
import pandas as pd
import plotly.express as px

def show_support_tier(df):
    st.header("Feature & Support Tier")
    
    # Add sorting option
    sort_option = st.selectbox(
        "Sort by:",
        ["Default", "Highest to Lowest", "Lowest to Highest"],
        key="sort_metric4"
    )
    
    # Prepare data for interactive chart
    feature_tier = df.groupby(['Features Category', 'IT Support Tier']).size().reset_index(name='Count')
    
    # Calculate total count per feature for sorting
    feature_totals = feature_tier.groupby('Features Category')['Count'].sum().reset_index()
    feature_totals.columns = ['Features Category', 'Total']
    
    # Apply sorting based on selected option
    if sort_option == "Default":
        feature_totals = feature_totals.sort_values('Features Category')
    elif sort_option == "Highest to Lowest":
        feature_totals = feature_totals.sort_values('Total', ascending=False)
    elif sort_option == "Lowest to Highest":
        feature_totals = feature_totals.sort_values('Total', ascending=True)
    
    # Reorder feature_tier based on sorted feature_totals
    feature_tier['Features Category'] = pd.Categorical(
        feature_tier['Features Category'],
        categories=feature_totals['Features Category'].tolist(),
        ordered=True
    )
    feature_tier = feature_tier.sort_values('Features Category')
    
    st.subheader("Interactive Chart: IT Support Tier by Feature Category")
    st.write("*Click on the legend items to show/hide specific support tiers*")
    
    # Create interactive bar chart
    fig = px.bar(feature_tier, 
                 x='Features Category',
                 y='Count',
                 color='IT Support Tier',
                 title='IT Support Tier Distribution by Feature Category',
                 barmode='stack',
                 hover_data=['Count'])
    
    fig.update_layout(
        height=600,
        xaxis_title='Features Category',
        yaxis_title='Count',
        legend_title_text='IT Support Tier',
        xaxis_tickangle=-45
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.write("---")
    
    pivot = pd.pivot_table(df, index='Features Category', columns='IT Support Tier', aggfunc='size', fill_value=0)
    st.dataframe(pivot)
    st.write("---")
    
    st.subheader("Feature & Support Tier Details")
    
    # Add filters for the table
    col1, col2 = st.columns(2)
    with col1:
        feature_options = ['All'] + sorted(feature_tier['Features Category'].unique().tolist())
        selected_feature = st.selectbox('Feature Category:', feature_options, key='filter_feature_tier_table')
    with col2:
        tier_options = ['All'] + sorted(feature_tier['IT Support Tier'].unique().tolist())
        selected_tier = st.selectbox('Support Tier:', tier_options, key='filter_tier_feature_table')
    
    # Apply filters
    filtered_feature_tier = feature_tier.copy()
    if selected_feature != 'All':
        filtered_feature_tier = filtered_feature_tier[filtered_feature_tier['Features Category'] == selected_feature]
    if selected_tier != 'All':
        filtered_feature_tier = filtered_feature_tier[filtered_feature_tier['IT Support Tier'] == selected_tier]
    
    table_data = filtered_feature_tier.sort_values('Count', ascending=False).reset_index(drop=True)
    table_data.index = table_data.index + 1
    st.dataframe(table_data)

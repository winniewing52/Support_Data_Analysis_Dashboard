import streamlit as st
import plotly.express as px

def show_feature_support_tier(df):
    st.header("📊 Support Tier Overview")
    
    # Count occurrences of each support tier
    tier_counts = df['IT Support Tier'].value_counts().reset_index()
    tier_counts.columns = ['IT Support Tier', 'Count']
    
    st.subheader("Support Tier Distribution")
    st.write("*Distribution of requests across IT Support Tiers: BUG, CODE, FIRST LAYER, OPERATION, REQUEST, SECOND LAYER, TRAINING*")
    
    # Create interactive pie chart
    fig = px.pie(tier_counts, 
                 values='Count',
                 names='IT Support Tier',
                 title='IT Support Tier Distribution',
                 color_discrete_sequence=px.colors.qualitative.Set3)
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    fig.update_layout(
        height=600,
        legend_title_text='IT Support Tier'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.write("---")
    
    st.subheader("Support Tier Summary")
    tier_display = tier_counts.reset_index(drop=True)
    tier_display.index = tier_display.index + 1
    st.dataframe(tier_display)
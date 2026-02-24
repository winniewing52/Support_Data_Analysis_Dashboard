import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import re
from .metric2_most_features import show_most_features
from .metric3_feature_support_tier import show_feature_support_tier
from .metric4_support_tier import show_support_tier
from .metric5_top_sales_curiosity import show_top_sales_curiosity
from .metric6_sales_support_tier import show_sales_support_tier

def sort_for_bar_chart(df_in: pd.DataFrame, sort_col: str, order: str, x_col: str = None) -> pd.DataFrame:
    """Sort dataframe for bar chart display"""
    if df_in.empty:
        return df_in
    
    if order == "Default":
        # Sort by x-axis column alphabetically
        if x_col and x_col in df_in.columns:
            return df_in.sort_values(x_col)
        return df_in
    
    if sort_col not in df_in.columns:
        return df_in
    
    ascending = order == "Lowest to Highest"
    return df_in.sort_values(sort_col, ascending=ascending)


def show_week_comparison(df):
    """
    Compare metrics between different weeks within the same dataset.
    Extracts week numbers from various formats: W1, W2, Week 1, 1, etc.
    """
    st.header("📊 Week-to-Week Comparison")
    
    # Check if Week column exists
    week_col = 'Week' if 'Week' in df.columns else df.columns[0]
    
    if week_col not in df.columns:
        st.error("❌ No 'Week' column found in the dataset.")
        return
    
    # Extract all week numbers from the data
    def extract_week_number(value):
        """Extract week number from various formats: JAN W1, W2, Week 1, 1, etc."""
        if pd.isna(value):
            return None
        val_str = str(value).strip()
        # Match patterns like: JAN W1, W2, w2, Week 1, week 1, or just 1
        # This handles formats: "JAN W1", "W1", "Week 1", "1", etc.
        match = re.search(r'[Ww](?:eek)?\s*(\d+)|(\d+)', val_str)
        if match:
            week_num = match.group(1) or match.group(2)
            return int(week_num)
        return None
    
    # Create a new column with extracted week numbers
    df_with_weeks = df.copy()
    df_with_weeks['Week_Number'] = df_with_weeks[week_col].apply(extract_week_number)
    
    # Remove rows without valid week numbers
    df_with_weeks = df_with_weeks[df_with_weeks['Week_Number'].notna()]
    
    if df_with_weeks.empty:
        st.warning("⚠️ No valid week numbers found in the dataset.")
        return
    
    # Get available weeks sorted
    available_weeks = sorted(df_with_weeks['Week_Number'].unique())
    
    if len(available_weeks) < 2:
        st.info("ℹ️ Need at least 2 weeks of data to make a comparison.")
        return
    
    st.info(f"📅 Available weeks: {', '.join(['Week ' + str(w) for w in available_weeks])}")
    
    # Week selection
    col1, col2 = st.columns(2)
    
    with col1:
        week1 = st.selectbox(
            "Select First Week:",
            available_weeks,
            index=0,
            format_func=lambda x: f"Week {x}",
            key="week1_selector"
        )
    
    with col2:
        # Default to the next week if available, otherwise the last week
        default_week2_idx = min(1, len(available_weeks) - 1)
        week2 = st.selectbox(
            "Select Second Week:",
            available_weeks,
            index=default_week2_idx,
            format_func=lambda x: f"Week {x}",
            key="week2_selector"
        )
    
    if week1 == week2:
        st.warning("⚠️ Please select two different weeks to compare.")
        return
    
    # Filter data for selected weeks
    df_week1 = df_with_weeks[df_with_weeks['Week_Number'] == week1]
    df_week2 = df_with_weeks[df_with_weeks['Week_Number'] == week2]
    
    st.markdown("---")
    
    # Overview Metrics
    st.subheader(f"📈 Overview: Week {week1} vs Week {week2}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        q1 = len(df_week1)
        q2 = len(df_week2)
        delta = q2 - q1
        delta_pct = ((q2 - q1) / q1 * 100) if q1 > 0 else 0
        st.metric(
            "Total Questions",
            f"{q2}",
            f"{delta:+d} ({delta_pct:+.1f}%)",
            delta_color="normal"
        )
    
    with col2:
        if 'Merchants' in df.columns:
            m1 = df_week1['Merchants'].nunique()
            m2 = df_week2['Merchants'].nunique()
            delta = m2 - m1
            delta_pct = ((m2 - m1) / m1 * 100) if m1 > 0 else 0
            st.metric(
                "Unique Merchants",
                f"{m2}",
                f"{delta:+d} ({delta_pct:+.1f}%)",
                delta_color="normal"
            )
    
    st.markdown("---")
    
    # Create tabs for different comparisons
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Overview",
        "Top Features",
        "Support Tier Overview",
        "Feature & Support Tier",
        "Top Sales",
        "Sales Support Tier"
    ])
    
    with tab1:
        st.subheader(f"📊 Detailed Overview: Week {week1} vs Week {week2}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"### Week {week1} Statistics")
            st.metric("Total Questions", len(df_week1))
            if 'Merchants' in df.columns:
                st.metric("Unique Merchants", df_week1['Merchants'].nunique())
        
        with col2:
            st.write(f"### Week {week2} Statistics")
            st.metric("Total Questions", len(df_week2))
            if 'Merchants' in df.columns:
                st.metric("Unique Merchants", df_week2['Merchants'].nunique())
    
    with tab2:
        st.subheader(f"🎯 Top Features Comparison: Week {week1} vs Week {week2}")
        
        features_list = [
            "Appointment", "Attendance", "Classroom", "E-Invoice", "Expenses", "General", "HARDWARE", "History", "Inventory", "Mall Integration", "Member", "Menu", "Message", "Online", "Booking", "Order", "Queue", "Receipt", "Report", "Roster", "Settings", "Shift", "Report", "SQL Integration", "Staff", "Tunai App", "Tunai Biz", "Tunai Staff", "Voucher", "Walk-in"
        ]
        
        # Get feature counts for both weeks
        features_w1 = df_week1['Features Category'].value_counts().reset_index()
        features_w1.columns = ['Feature', f'Week {week1}']
        features_w2 = df_week2['Features Category'].value_counts().reset_index()
        features_w2.columns = ['Feature', f'Week {week2}']
        
        # Merge the two dataframes
        features_comparison = features_w1.merge(features_w2, on='Feature', how='outer').fillna(0)
        features_comparison = features_comparison[features_comparison['Feature'].isin(features_list)]
        
        # Sort by total
        features_comparison['Total'] = features_comparison[f'Week {week1}'] + features_comparison[f'Week {week2}']
        features_comparison = features_comparison.sort_values('Total', ascending=False)
        
        # Add sort control
        sort_order_features = st.selectbox(
            "Bar chart sort",
            ["Default", "Highest to Lowest", "Lowest to Highest"],
            key="features_bar_sort_week"
        )
        features_chart_data = sort_for_bar_chart(
            features_comparison,
            f'Week {week2}',
            sort_order_features,
            x_col='Feature'
        )
        
        # Create grouped bar chart
        fig = px.bar(features_chart_data, x='Feature', y=[f'Week {week1}', f'Week {week2}'],
                     title='Feature Requests Comparison',
                     barmode='group',
                     labels={'value': 'Count', 'variable': 'Week'})
        fig.update_layout(xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader(f"📊 Support Tier Overview Comparison: Week {week1} vs Week {week2}")
        
        # Get support tier counts for both weeks
        tier_w1 = df_week1['IT Support Tier'].value_counts().reset_index()
        tier_w1.columns = ['IT Support Tier', f'Week {week1}']
        tier_w2 = df_week2['IT Support Tier'].value_counts().reset_index()
        tier_w2.columns = ['IT Support Tier', f'Week {week2}']
        
        # Merge the two dataframes
        tier_comparison = tier_w1.merge(tier_w2, on='IT Support Tier', how='outer').fillna(0)
        
        # Add sort control
        sort_order_tier = st.selectbox(
            "Bar chart sort",
            ["Default", "Highest to Lowest", "Lowest to Highest"],
            key="tier_bar_sort_week"
        )
        tier_chart_data = sort_for_bar_chart(
            tier_comparison,
            f'Week {week2}',
            sort_order_tier,
            x_col='IT Support Tier'
        )
        
        # Create grouped bar chart
        fig = px.bar(tier_chart_data, x='IT Support Tier', y=[f'Week {week1}', f'Week {week2}'],
                     title='IT Support Tier Distribution Comparison',
                     barmode='group',
                     labels={'value': 'Count', 'variable': 'Week'})
        fig.update_layout(xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader(f"🔗 Feature & Support Tier Comparison: Week {week1} vs Week {week2}")
        
        # Build one stacked chart comparing two weeks (same style as metric4)
        feature_tier_w1 = df_week1.groupby(['Features Category', 'IT Support Tier']).size().reset_index(name='Count')
        feature_tier_w1['Week'] = f"Week {week1}"
        feature_tier_w2 = df_week2.groupby(['Features Category', 'IT Support Tier']).size().reset_index(name='Count')
        feature_tier_w2['Week'] = f"Week {week2}"
        feature_tier_combined = pd.concat([feature_tier_w1, feature_tier_w2], ignore_index=True)
        
        sort_order_feature_tier = st.selectbox(
            "Bar chart sort",
            ["Default", "Highest to Lowest", "Lowest to Highest"],
            key="feature_tier_bar_sort_week"
        )
        
        if feature_tier_combined.empty:
            st.info("No feature or support tier data available")
        else:
            week2_label = f"Week {week2}"
            week1_label = f"Week {week1}"
            
            if sort_order_feature_tier == "Default":
                feature_totals = (
                    feature_tier_combined[feature_tier_combined['Week'] == week2_label]
                    .groupby('Features Category')['Count']
                    .sum()
                    .sort_index()
                )
            else:
                feature_totals = (
                    feature_tier_combined[feature_tier_combined['Week'] == week2_label]
                    .groupby('Features Category')['Count']
                    .sum()
                    .sort_values(ascending=sort_order_feature_tier == "Lowest to Highest")
                )
            unique_features = feature_totals.index.tolist()
            
            st.subheader("Interactive Chart: IT Support Tier by Feature Category")
            st.write("*Click on the legend items to show/hide specific support tiers*")
            
            fig = go.Figure()
            for tier in feature_tier_combined['IT Support Tier'].unique():
                x_labels = []
                y_values = []
                for feature in unique_features:
                    w1_data = feature_tier_combined[
                        (feature_tier_combined['Features Category'] == feature) &
                        (feature_tier_combined['IT Support Tier'] == tier) &
                        (feature_tier_combined['Week'] == week1_label)
                    ]
                    x_labels.append(f"{feature} ({week1_label})")
                    y_values.append(w1_data['Count'].values[0] if len(w1_data) > 0 else 0)
                    
                    w2_data = feature_tier_combined[
                        (feature_tier_combined['Features Category'] == feature) &
                        (feature_tier_combined['IT Support Tier'] == tier) &
                        (feature_tier_combined['Week'] == week2_label)
                    ]
                    x_labels.append(f"{feature} ({week2_label})")
                    y_values.append(w2_data['Count'].values[0] if len(w2_data) > 0 else 0)
                
                fig.add_trace(go.Bar(
                    x=x_labels,
                    y=y_values,
                    name=tier
                ))
            
            fig.update_layout(
                title=f'IT Support Tier Distribution by Feature Category - {week1_label} vs {week2_label}',
                barmode='stack',
                xaxis_tickangle=-45,
                height=600,
                xaxis_title='Features Category',
                yaxis_title='Count',
                legend_title_text='IT Support Tier (Click to toggle)'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.subheader(f"🏆 Top Sales Comparison: Week {week1} vs Week {week2}")
        
        sales_list = ["Danny", "Dylan", "Erica", "Hazwan", "Jun", "Kyle", "Old Sales", "Qis", "Raymond", "Tammy", "Tom"]
        
        # Get sales counts for both weeks
        sales_w1 = df_week1['Sales'].value_counts().reset_index()
        sales_w1.columns = ['Sales', f'Week {week1}']
        sales_w2 = df_week2['Sales'].value_counts().reset_index()
        sales_w2.columns = ['Sales', f'Week {week2}']
        
        # Merge the two dataframes
        sales_comparison = sales_w1.merge(sales_w2, on='Sales', how='outer').fillna(0)
        sales_comparison = sales_comparison[sales_comparison['Sales'].isin(sales_list)]
        
        # Sort by total
        sales_comparison['Total'] = sales_comparison[f'Week {week1}'] + sales_comparison[f'Week {week2}']
        sales_comparison = sales_comparison.sort_values('Total', ascending=False)
        
        # Add sort control
        sort_order_sales = st.selectbox(
            "Bar chart sort",
            ["Default", "Highest to Lowest", "Lowest to Highest"],
            key="sales_bar_sort_week"
        )
        sales_chart_data = sort_for_bar_chart(
            sales_comparison,
            f'Week {week2}',
            sort_order_sales,
            x_col='Sales'
        )
        
        # Create grouped bar chart
        fig = px.bar(sales_chart_data, x='Sales', y=[f'Week {week1}', f'Week {week2}'],
                     title='Questions Asked by Sales Comparison',
                     barmode='group',
                     labels={'value': 'Count', 'variable': 'Week'})
        fig.update_layout(xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab6:
        st.subheader(f"💼 Sales Support Tier Comparison: Week {week1} vs Week {week2}")
        
        # Build one stacked chart comparing two weeks (same style as metric8)
        sales_tier_w1 = df_week1.groupby(['Sales', 'IT Support Tier']).size().reset_index(name='Count')
        sales_tier_w1['Week'] = f"Week {week1}"
        sales_tier_w2 = df_week2.groupby(['Sales', 'IT Support Tier']).size().reset_index(name='Count')
        sales_tier_w2['Week'] = f"Week {week2}"
        sales_tier_combined = pd.concat([sales_tier_w1, sales_tier_w2], ignore_index=True)
        
        sort_order_sales_tier = st.selectbox(
            "Bar chart sort",
            ["Default", "Highest to Lowest", "Lowest to Highest"],
            key="sales_tier_bar_sort_week"
        )
        
        if sales_tier_combined.empty:
            st.info("No sales or support tier data available")
        else:
            week2_label = f"Week {week2}"
            week1_label = f"Week {week1}"
            
            if sort_order_sales_tier == "Default":
                sales_totals = (
                    sales_tier_combined[sales_tier_combined['Week'] == week2_label]
                    .groupby('Sales')['Count']
                    .sum()
                    .sort_index()
                )
            else:
                sales_totals = (
                    sales_tier_combined[sales_tier_combined['Week'] == week2_label]
                    .groupby('Sales')['Count']
                    .sum()
                    .sort_values(ascending=sort_order_sales_tier == "Lowest to Highest")
                )
            unique_sales = sales_totals.index.tolist()
            
            st.subheader("Interactive Chart: IT Support Tier by Sales")
            st.write("*Click on the legend items to show/hide specific support tiers*")
            
            fig = go.Figure()
            for tier in sales_tier_combined['IT Support Tier'].unique():
                x_labels = []
                y_values = []
                for sales in unique_sales:
                    w1_data = sales_tier_combined[
                        (sales_tier_combined['Sales'] == sales) &
                        (sales_tier_combined['IT Support Tier'] == tier) &
                        (sales_tier_combined['Week'] == week1_label)
                    ]
                    x_labels.append(f"{sales} ({week1_label})")
                    y_values.append(w1_data['Count'].values[0] if len(w1_data) > 0 else 0)
                    
                    w2_data = sales_tier_combined[
                        (sales_tier_combined['Sales'] == sales) &
                        (sales_tier_combined['IT Support Tier'] == tier) &
                        (sales_tier_combined['Week'] == week2_label)
                    ]
                    x_labels.append(f"{sales} ({week2_label})")
                    y_values.append(w2_data['Count'].values[0] if len(w2_data) > 0 else 0)
                
                fig.add_trace(go.Bar(
                    x=x_labels,
                    y=y_values,
                    name=tier
                ))
            
            fig.update_layout(
                title=f'IT Support Tier Distribution by Sales Person - {week1_label} vs {week2_label}',
                barmode='stack',
                xaxis_tickangle=-45,
                height=600,
                xaxis_title='Sales Person',
                yaxis_title='Number of Questions',
                legend_title_text='IT Support Tier (Click to toggle)'
            )
            st.plotly_chart(fig, use_container_width=True)
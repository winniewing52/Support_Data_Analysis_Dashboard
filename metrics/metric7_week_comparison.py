import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re

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
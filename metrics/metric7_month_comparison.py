import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import re
from urllib.parse import quote

def show_month_comparison(data_source, uploaded_file, google_sheet_url, sheet_gid=None):
    """
    Compare metrics between two months, where each month is a separate sheet.
    - Excel: compares two sheets in the same workbook
    - Google Sheets: compares two sheets by name or GID
    - CSV: compares two CSV files
    """
    st.header("📅 Month-to-Month Comparison (by Sheet)")

    def sort_for_bar_chart(df_in: pd.DataFrame, sort_col: str, order: str) -> pd.DataFrame:
        if df_in.empty or sort_col not in df_in.columns:
            return df_in
        ascending = order == "Lowest"
        return df_in.sort_values(sort_col, ascending=ascending)

    def clean_df(df_in: pd.DataFrame) -> pd.DataFrame:
        df_out = df_in.copy()
        df_out.columns = df_out.columns.astype(str).str.strip()
        df_out = df_out.loc[:, ~df_out.columns.str.match(r"^Unnamed", na=False)]
        df_out = df_out.dropna(how="all")
        with pd.option_context("future.no_silent_downcasting", True):
            df_out = df_out.convert_dtypes()
        return df_out

    def load_excel_sheet(file, sheet_name):
        try:
            df_sheet = pd.read_excel(file, sheet_name=sheet_name)
            return clean_df(df_sheet)
        except Exception as e:
            st.error(f"❌ Error loading Excel sheet '{sheet_name}': {str(e)}")
            return None

    def load_google_sheet(url, sheet_name=None, gid=None):
        try:
            match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
            if not match:
                st.error("❌ Invalid Google Sheets URL. Please check the URL and try again.")
                return None
            sheet_id = match.group(1)

            if sheet_name:
                encoded_sheet_name = quote(sheet_name)
                csv_export_url = (
                    f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?"
                    f"tqx=out:csv&sheet={encoded_sheet_name}"
                )
            else:
                if gid is None:
                    gid_match = re.search(r'(?:[?&#])gid=(\d+)', url)
                    gid = gid_match.group(1) if gid_match else None
                if gid:
                    csv_export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
                else:
                    csv_export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

            df = pd.read_csv(csv_export_url)
            return clean_df(df)
        except Exception as e:
            st.error(f"❌ Error loading Google Sheet: {str(e)}")
            st.info("💡 Make sure the Google Sheet is set to 'Anyone with the link can view'")
            return None

    df1 = None
    df2 = None
    month1_label = "Month 1"
    month2_label = "Month 2"

    if data_source == "📁 Upload File":
        if uploaded_file is None:
            st.info("Please upload a file to compare.")
            return

        filename = getattr(uploaded_file, "name", "uploaded")
        suffix = Path(filename).suffix.lower().lstrip(".")

        if suffix == "csv":
            st.info("📄 CSV files don’t have sheets. Upload two CSVs to compare months.")
            col1, col2 = st.columns(2)
            with col1:
                csv1 = uploaded_file
                month1_label = st.text_input("Month 1 Label", value=Path(filename).stem, key="csv_month1_label")
            with col2:
                csv2 = st.file_uploader("Upload Month 2 CSV", type=["csv"], key="month2_csv")
                month2_label = st.text_input("Month 2 Label", value="Month 2", key="csv_month2_label")

            if csv2 is None:
                st.warning("Please upload the second CSV to compare.")
                return

            df1 = clean_df(pd.read_csv(csv1))
            df2 = clean_df(pd.read_csv(csv2))

        else:
            try:
                xls = pd.ExcelFile(uploaded_file, engine="openpyxl")
            except Exception:
                xls = pd.ExcelFile(uploaded_file)

            sheet_names = xls.sheet_names
            if len(sheet_names) < 2:
                st.warning("⚠️ This Excel file has only one sheet. Add another sheet to compare months.")
                return

            col1, col2 = st.columns(2)
            with col1:
                sheet1 = st.selectbox("Select Month 1 Sheet", sheet_names, index=0, key="month1_sheet")
                month1_label = sheet1
            with col2:
                sheet2 = st.selectbox(
                    "Select Month 2 Sheet",
                    sheet_names,
                    index=1 if len(sheet_names) > 1 else 0,
                    key="month2_sheet"
                )
                month2_label = sheet2

            if sheet1 == sheet2:
                st.error("❌ Please select two different sheets to compare")
                return

            df1 = load_excel_sheet(uploaded_file, sheet1)
            df2 = load_excel_sheet(uploaded_file, sheet2)

    else:
        if not google_sheet_url:
            st.info("Please enter a Google Sheet URL to compare.")
            return

        st.info("💡 Compare two sheets by **Sheet Name** (e.g., Jan, Feb) or by **GID**.")
        method = st.radio("Select Sheet Identifier", ["Sheet Name", "GID"], horizontal=True)

        col1, col2 = st.columns(2)
        if method == "Sheet Name":
            with col1:
                sheet1_name = st.text_input("Month 1 Sheet Name", value="Jan", key="gsheet_name_1")
                month1_label = sheet1_name
            with col2:
                sheet2_name = st.text_input("Month 2 Sheet Name", value="Feb", key="gsheet_name_2")
                month2_label = sheet2_name

            if sheet1_name == sheet2_name:
                st.error("❌ Please enter two different sheet names to compare")
                return

            df1 = load_google_sheet(google_sheet_url, sheet_name=sheet1_name)
            df2 = load_google_sheet(google_sheet_url, sheet_name=sheet2_name)
        else:
            with col1:
                sheet1_gid = st.text_input("Month 1 GID", value=str(sheet_gid or "0"), key="gsheet_gid_1")
                month1_label = f"GID {sheet1_gid}"
            with col2:
                sheet2_gid = st.text_input("Month 2 GID", value="", key="gsheet_gid_2")
                month2_label = f"GID {sheet2_gid}" if sheet2_gid else "Month 2"

            if not sheet2_gid:
                st.warning("Please enter the second GID to compare.")
                return

            if sheet1_gid == sheet2_gid:
                st.error("❌ Please enter two different GIDs to compare")
                return

            df1 = load_google_sheet(google_sheet_url, gid=sheet1_gid)
            df2 = load_google_sheet(google_sheet_url, gid=sheet2_gid)

    if df1 is None or df2 is None or df1.empty or df2.empty:
        st.warning("⚠️ One or both sheets are empty or could not be loaded.")
        return
    
    # Display comparison metrics
    st.markdown("---")
    st.subheader(f"📊 {month1_label} vs {month2_label}")
    
    # Calculate key metrics
    metric1_total = len(df1)
    metric2_total = len(df2)
    questions_change = metric2_total - metric1_total
    questions_change_pct = (questions_change / metric1_total * 100) if metric1_total > 0 else 0
    
    metric1_merchants = df1['Merchants'].nunique() if 'Merchants' in df1.columns else 0
    metric2_merchants = df2['Merchants'].nunique() if 'Merchants' in df2.columns else 0
    merchants_change = metric2_merchants - metric1_merchants
    
    # Show individual metric cards for quick reference
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Total Questions",
            metric2_total,
            f"{questions_change:+d} ({questions_change_pct:+.1f}%)"
        )
    
    with col2:
        st.metric(
            "Total Merchants",
            metric2_merchants,
            f"{merchants_change:+d}"
        )
    
    st.markdown("---")
    
    # Detailed comparison tables
    comparison_tabs = st.tabs([
        "Overview",
        "Top Feature Asked by Merchant",
        "Support Tier Overview",
        "Feature & Support Tier",
        "Top Sales",
        "IT Support Tier for Each Sales"
    ])
    
    with comparison_tabs[0]:
        st.subheader("Detailed Comparison")
        summary_data = {
            "Metric": ["Total Questions", "Total Merchants"],
            month1_label: [metric1_total, metric1_merchants],
            month2_label: [metric2_total, metric2_merchants]
        }
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    with comparison_tabs[1]:
        st.subheader("Most Features Asked by Merchant")
        if 'Features Category' in df1.columns and 'Features Category' in df2.columns:
            # Get feature counts for both months
            feature_counts1 = df1['Features Category'].value_counts().head(10).reset_index()
            feature_counts1.columns = ['Feature', f'{month1_label}']
            
            feature_counts2 = df2['Features Category'].value_counts().head(10).reset_index()
            feature_counts2.columns = ['Feature', f'{month2_label}']
            
            # Merge for comparison
            features_comparison = feature_counts1.merge(feature_counts2, on='Feature', how='outer').fillna(0)
            features_comparison['Change'] = features_comparison[f'{month2_label}'] - features_comparison[f'{month1_label}']
            features_comparison = features_comparison.sort_values(f'{month2_label}', ascending=False).head(10)
            features_comparison.index = features_comparison.index + 1
            
            # Bar chart comparison
            if not features_comparison.empty:
                sort_order_features = st.selectbox(
                    "Bar chart sort (by Month 2 count)",
                    ["Highest", "Lowest"],
                    key="features_bar_sort"
                )
                features_chart_data = sort_for_bar_chart(
                    features_comparison,
                    f'{month2_label}',
                    sort_order_features
                )
                fig = go.Figure(data=[
                    go.Bar(name=month1_label, x=features_chart_data['Feature'], y=features_chart_data[f'{month1_label}']),
                    go.Bar(name=month2_label, x=features_chart_data['Feature'], y=features_chart_data[f'{month2_label}'])
                ])
                fig.update_layout(
                    title=f"Top Features: {month1_label} vs {month2_label}",
                    barmode='group',
                    xaxis_title="Feature",
                    yaxis_title="Count",
                    hovermode='x unified',
                    height=400,
                    xaxis_tickangle=-45
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(features_comparison, use_container_width=True)
            
            st.write("---")
            
            st.subheader("Feature Requests by Merchant")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**{month1_label}**")
                pivot1 = pd.pivot_table(df1, index='Merchants', columns='Features Category', aggfunc='size', fill_value=0)
                st.dataframe(pivot1)
            
            with col2:
                st.write(f"**{month2_label}**")
                pivot2 = pd.pivot_table(df2, index='Merchants', columns='Features Category', aggfunc='size', fill_value=0)
                st.dataframe(pivot2)
        else:
            st.info("No feature or merchant data available")
    
    with comparison_tabs[2]:
        st.subheader("Support Tier Overview")
        if 'IT Support Tier' in df1.columns and 'IT Support Tier' in df2.columns:
            # Get tier counts for both months
            tier1 = df1['IT Support Tier'].value_counts().reset_index()
            tier1.columns = ['IT Support Tier', f'{month1_label}']
            
            tier2 = df2['IT Support Tier'].value_counts().reset_index()
            tier2.columns = ['IT Support Tier', f'{month2_label}']
            
            # Merge for comparison
            tier_comparison = tier1.merge(tier2, on='IT Support Tier', how='outer').fillna(0)
            tier_comparison['Change'] = tier_comparison[f'{month2_label}'] - tier_comparison[f'{month1_label}']
            tier_comparison.index = tier_comparison.index + 1
            
            # Bar chart comparison
            if not tier_comparison.empty:
                sort_order_tier = st.selectbox(
                    "Bar chart sort (by Month 2 count)",
                    ["Highest", "Lowest"],
                    key="tier_bar_sort"
                )
                tier_chart_data = sort_for_bar_chart(
                    tier_comparison,
                    f'{month2_label}',
                    sort_order_tier
                )
                fig = go.Figure(data=[
                    go.Bar(name=month1_label, x=tier_chart_data['IT Support Tier'], y=tier_chart_data[f'{month1_label}']),
                    go.Bar(name=month2_label, x=tier_chart_data['IT Support Tier'], y=tier_chart_data[f'{month2_label}'])
                ])
                fig.update_layout(
                    title=f"Support Tier Distribution: {month1_label} vs {month2_label}",
                    barmode='group',
                    xaxis_title="IT Support Tier",
                    yaxis_title="Count",
                    hovermode='x unified',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(tier_comparison, use_container_width=True)
        else:
            st.info("No support tier data available")
    
    with comparison_tabs[3]:
        st.subheader("Feature & Support Tier")
        if 'Features Category' in df1.columns and 'IT Support Tier' in df1.columns:
            # Prepare data for both months
            feature_tier1 = df1.groupby(['Features Category', 'IT Support Tier']).size().reset_index(name=f'{month1_label}')
            feature_tier2 = df2.groupby(['Features Category', 'IT Support Tier']).size().reset_index(name=f'{month2_label}')
            
            # Merge for comparison
            feature_tier_comparison = feature_tier1.merge(
                feature_tier2,
                on=['Features Category', 'IT Support Tier'],
                how='outer'
            ).fillna(0)
            
            st.write("*Click on the legend items to show/hide specific support tiers*")

            sort_order_feature_tier = st.selectbox(
                "Bar chart sort (by Month 2 total)",
                ["Highest", "Lowest"],
                key="feature_tier_bar_sort"
            )
            feature_totals = (
                feature_tier_comparison.groupby('Features Category')[f'{month2_label}']
                .sum()
                .sort_values(ascending=sort_order_feature_tier == "Lowest")
            )
            ordered_features = feature_totals.index.tolist()
            
            # Create comparison bar chart
            fig = go.Figure()
            
            for tier in feature_tier_comparison['IT Support Tier'].unique():
                tier_data = feature_tier_comparison[feature_tier_comparison['IT Support Tier'] == tier]
                tier_data = tier_data.set_index('Features Category').reindex(ordered_features).reset_index()
                fig.add_trace(go.Bar(
                    x=tier_data['Features Category'],
                    y=tier_data[f'{month1_label}'],
                    name=f'{tier} ({month1_label})'
                ))
            
            for tier in feature_tier_comparison['IT Support Tier'].unique():
                tier_data = feature_tier_comparison[feature_tier_comparison['IT Support Tier'] == tier]
                tier_data = tier_data.set_index('Features Category').reindex(ordered_features).reset_index()
                fig.add_trace(go.Bar(
                    x=tier_data['Features Category'],
                    y=tier_data[f'{month2_label}'],
                    name=f'{tier} ({month2_label})'
                ))
            
            fig.update_layout(
                title=f'Feature & Support Tier: {month1_label} vs {month2_label}',
                barmode='group',
                xaxis_title='Feature Category',
                yaxis_title='Count',
                height=500,
                xaxis_tickangle=-45,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.write("---")
            pivot = pd.pivot_table(feature_tier_comparison, index='Features Category', columns='IT Support Tier', values=[f'{month1_label}', f'{month2_label}'], aggfunc='sum', fill_value=0)
            st.dataframe(pivot)
        else:
            st.info("No feature or support tier data available")
    
    with comparison_tabs[4]:
        st.subheader("Top Sales Comparison")
        if 'Sales' in df1.columns and 'Sales' in df2.columns:
            sales1 = df1['Sales'].value_counts().head(10).reset_index()
            sales1.columns = ['Sales', f'{month1_label}']
            
            sales2 = df2['Sales'].value_counts().head(10).reset_index()
            sales2.columns = ['Sales', f'{month2_label}']
            
            sales_comparison = sales1.merge(sales2, on='Sales', how='outer').fillna(0)
            sales_comparison['Change'] = sales_comparison[f'{month2_label}'] - sales_comparison[f'{month1_label}']
            sales_comparison = sales_comparison.sort_values(f'{month2_label}', ascending=False).head(10)
            sales_comparison.index = sales_comparison.index + 1
            
            # Bar chart comparison
            if not sales_comparison.empty:
                sort_order_sales = st.selectbox(
                    "Bar chart sort (by Month 2 count)",
                    ["Highest", "Lowest"],
                    key="sales_bar_sort"
                )
                sales_chart_data = sort_for_bar_chart(
                    sales_comparison,
                    f'{month2_label}',
                    sort_order_sales
                )
                fig = go.Figure(data=[
                    go.Bar(name=month1_label, x=sales_chart_data['Sales'], y=sales_chart_data[f'{month1_label}']),
                    go.Bar(name=month2_label, x=sales_chart_data['Sales'], y=sales_chart_data[f'{month2_label}'])
                ])
                fig.update_layout(
                    title=f"Top Sales: {month1_label} vs {month2_label}",
                    barmode='group',
                    xaxis_title="Sales",
                    yaxis_title="Questions",
                    hovermode='x unified',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(sales_comparison, use_container_width=True)
        else:
            st.info("No sales data available")
    
    with comparison_tabs[5]:
        st.subheader("IT Support Tier for Each Sales")
        if 'Sales' in df1.columns and 'IT Support Tier' in df1.columns:
            # Prepare data for both months
            sales_tier1 = df1.groupby(['Sales', 'IT Support Tier']).size().reset_index(name='Count')
            sales_tier1['Month'] = month1_label
            sales_tier2 = df2.groupby(['Sales', 'IT Support Tier']).size().reset_index(name='Count')
            sales_tier2['Month'] = month2_label
            
            # Combine both months
            sales_tier_combined = pd.concat([sales_tier1, sales_tier2], ignore_index=True)
            
            # Create ordered x-axis labels
            sort_order_sales_tier = st.selectbox(
                "Bar chart sort (by Month 2 total)",
                ["Highest", "Lowest"],
                key="sales_tier_bar_sort"
            )
            sales_totals = (
                sales_tier_combined[sales_tier_combined['Month'] == month2_label]
                .groupby('Sales')['Count']
                .sum()
                .sort_values(ascending=sort_order_sales_tier == "Lowest")
            )
            unique_sales = sales_totals.index.tolist()
            ordered_labels = []
            for sales in unique_sales:
                ordered_labels.append(f"{sales} ({month1_label})")
                ordered_labels.append(f"{sales} ({month2_label})")
            
            st.subheader("Interactive Chart: IT Support Tier by Sales")
            st.write("*Click on the legend items to show/hide specific support tiers*")
            
            # Create interactive stacked bar chart for both months combined
            fig = go.Figure()
            
            for tier in sales_tier_combined['IT Support Tier'].unique():
                x_labels = []
                y_values = []
                
                for sales in unique_sales:
                    # Add month 1 data
                    m1_data = sales_tier_combined[
                        (sales_tier_combined['Sales'] == sales) &
                        (sales_tier_combined['IT Support Tier'] == tier) &
                        (sales_tier_combined['Month'] == month1_label)
                    ]
                    x_labels.append(f"{sales} ({month1_label})")
                    y_values.append(m1_data['Count'].values[0] if len(m1_data) > 0 else 0)
                    
                    # Add month 2 data
                    m2_data = sales_tier_combined[
                        (sales_tier_combined['Sales'] == sales) &
                        (sales_tier_combined['IT Support Tier'] == tier) &
                        (sales_tier_combined['Month'] == month2_label)
                    ]
                    x_labels.append(f"{sales} ({month2_label})")
                    y_values.append(m2_data['Count'].values[0] if len(m2_data) > 0 else 0)
                
                fig.add_trace(go.Bar(
                    x=x_labels,
                    y=y_values,
                    name=tier
                ))
            
            fig.update_layout(
                title=f'IT Support Tier Distribution by Sales Person - {month1_label} vs {month2_label}',
                barmode='stack',
                xaxis_tickangle=-45,
                height=600,
                xaxis_title='Sales Person',
                yaxis_title='Number of Questions',
                legend_title_text='IT Support Tier (Click to toggle)'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.write("---")
            
            # Month 1 Details
            st.subheader(f"Sales & IT Support Tier Details - {month1_label}")
            
            col1, col2 = st.columns(2)
            with col1:
                sales_options = ['All'] + sorted(sales_tier1['Sales'].unique().tolist())
                selected_sales_m1 = st.selectbox('Filter by Sales:', sales_options, key='filter_sales_tier_m1')
            with col2:
                tier_options = ['All'] + sorted(sales_tier1['IT Support Tier'].unique().tolist())
                selected_tier_m1 = st.selectbox('Filter by IT Support Tier:', tier_options, key='filter_tier_sales_m1')
            
            # Apply filters for month 1
            filtered_sales_tier_m1 = sales_tier1.copy()
            if selected_sales_m1 != 'All':
                filtered_sales_tier_m1 = filtered_sales_tier_m1[filtered_sales_tier_m1['Sales'] == selected_sales_m1]
            if selected_tier_m1 != 'All':
                filtered_sales_tier_m1 = filtered_sales_tier_m1[filtered_sales_tier_m1['IT Support Tier'] == selected_tier_m1]
            
            table_data_m1 = filtered_sales_tier_m1.sort_values('Count', ascending=False).reset_index(drop=True)
            table_data_m1.index = table_data_m1.index + 1
            st.dataframe(table_data_m1)
            
            st.write("---")
            
            # Month 2 Details
            st.subheader(f"Sales & IT Support Tier Details - {month2_label}")
            
            col1, col2 = st.columns(2)
            with col1:
                sales_options = ['All'] + sorted(sales_tier2['Sales'].unique().tolist())
                selected_sales_m2 = st.selectbox('Filter by Sales:', sales_options, key='filter_sales_tier_m2')
            with col2:
                tier_options = ['All'] + sorted(sales_tier2['IT Support Tier'].unique().tolist())
                selected_tier_m2 = st.selectbox('Filter by IT Support Tier:', tier_options, key='filter_tier_sales_m2')
            
            # Apply filters for month 2
            filtered_sales_tier_m2 = sales_tier2.copy()
            if selected_sales_m2 != 'All':
                filtered_sales_tier_m2 = filtered_sales_tier_m2[filtered_sales_tier_m2['Sales'] == selected_sales_m2]
            if selected_tier_m2 != 'All':
                filtered_sales_tier_m2 = filtered_sales_tier_m2[filtered_sales_tier_m2['IT Support Tier'] == selected_tier_m2]
            
            table_data_m2 = filtered_sales_tier_m2.sort_values('Count', ascending=False).reset_index(drop=True)
            table_data_m2.index = table_data_m2.index + 1
            st.dataframe(table_data_m2)
            
            st.write("---")
            
            # Show pivot tables for both months
            st.subheader("Support Tier Summary by Sales")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**{month1_label}**")
                pivot1 = pd.pivot_table(df1, index='Sales', columns='IT Support Tier', aggfunc='size', fill_value=0)
                st.dataframe(pivot1)
            with col2:
                st.write(f"**{month2_label}**")
                pivot2 = pd.pivot_table(df2, index='Sales', columns='IT Support Tier', aggfunc='size', fill_value=0)
                st.dataframe(pivot2)
        else:
            st.info("No sales or support tier data available")

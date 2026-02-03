import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import re

def show_month_comparison(data_source, uploaded_file, google_sheet_url, sheet_gid=None):
    """
    Compare metrics between two months, where each month is a separate sheet.
    - Excel: compares two sheets in the same workbook
    - Google Sheets: compares two sheets by name or GID
    - CSV: compares two CSV files
    """
    st.header("📅 Month-to-Month Comparison (by Sheet)")

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
                csv_export_url = (
                    f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?"
                    f"tqx=out:csv&sheet={sheet_name}"
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
    
    # Key metrics comparison
    col1, col2 = st.columns(2)
    
    with col1:
        metric1_total = len(df1)
        metric2_total = len(df2)
        change = metric2_total - metric1_total
        change_pct = (change / metric1_total * 100) if metric1_total > 0 else 0
        st.metric(
            "Total Questions",
            metric2_total,
            f"{change:+d} ({change_pct:+.1f}%)"
        )
    
    with col2:
        metric1_merchants = df1['Merchants'].nunique() if 'Merchants' in df1.columns else 0
        metric2_merchants = df2['Merchants'].nunique() if 'Merchants' in df2.columns else 0
        change = metric2_merchants - metric1_merchants
        st.metric(
            "Total Merchants",
            metric2_merchants,
            f"{change:+d}"
        )

    st.markdown("---")
    
    # Detailed comparison tables
    comparison_tabs = st.tabs(["Overview", "Top Merchants", "Top Sales", "Top Features", "Support Tier"])
    
    with comparison_tabs[0]:
        st.subheader("Detailed Comparison")
        comparison_data = {
            "Metric": [
                "Total Questions",
                "Unique Merchants",
                "Unique Sales",
                "Unique Features",
                "Avg Questions per Merchant"
            ],
            month1_label: [
                len(df1),
                df1['Merchants'].nunique() if 'Merchants' in df1.columns else 0,
                df1['Sales'].nunique() if 'Sales' in df1.columns else 0,
                df1['Feature'].nunique() if 'Feature' in df1.columns else 0,
                f"{len(df1) / (df1['Merchants'].nunique() if df1['Merchants'].nunique() > 0 else 1):.2f}" if 'Merchants' in df1.columns else "N/A"
            ],
            month2_label: [
                len(df2),
                df2['Merchants'].nunique() if 'Merchants' in df2.columns else 0,
                df2['Sales'].nunique() if 'Sales' in df2.columns else 0,
                df2['Feature'].nunique() if 'Feature' in df2.columns else 0,
                f"{len(df2) / (df2['Merchants'].nunique() if df2['Merchants'].nunique() > 0 else 1):.2f}" if 'Merchants' in df2.columns else "N/A"
            ]
        }
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True)
    
    with comparison_tabs[1]:
        st.subheader("Top Merchants Comparison")
        if 'Merchants' in df1.columns and 'Merchants' in df2.columns:
            merchants1 = df1['Merchants'].value_counts().head(10).reset_index()
            merchants1.columns = ['Merchant', f'{month1_label}']
            
            merchants2 = df2['Merchants'].value_counts().head(10).reset_index()
            merchants2.columns = ['Merchant', f'{month2_label}']
            
            merchants_comparison = merchants1.merge(merchants2, on='Merchant', how='outer').fillna(0)
            merchants_comparison['Change'] = merchants_comparison[f'{month2_label}'] - merchants_comparison[f'{month1_label}']
            merchants_comparison = merchants_comparison.sort_values(f'{month2_label}', ascending=False).head(10)
            merchants_comparison.index = merchants_comparison.index + 1
            
            st.dataframe(merchants_comparison, use_container_width=True)
            
            # Bar chart comparison
            if not merchants_comparison.empty:
                fig = go.Figure(data=[
                    go.Bar(name=month1_label, x=merchants_comparison['Merchant'], y=merchants_comparison[f'{month1_label}']),
                    go.Bar(name=month2_label, x=merchants_comparison['Merchant'], y=merchants_comparison[f'{month2_label}'])
                ])
                fig.update_layout(
                    title=f"Top Merchants: {month1_label} vs {month2_label}",
                    barmode='group',
                    xaxis_title="Merchant",
                    yaxis_title="Questions",
                    hovermode='x unified',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No merchant data available")
    
    with comparison_tabs[2]:
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
            
            st.dataframe(sales_comparison, use_container_width=True)
            
            # Bar chart comparison
            if not sales_comparison.empty:
                fig = go.Figure(data=[
                    go.Bar(name=month1_label, x=sales_comparison['Sales'], y=sales_comparison[f'{month1_label}']),
                    go.Bar(name=month2_label, x=sales_comparison['Sales'], y=sales_comparison[f'{month2_label}'])
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
        else:
            st.info("No sales data available")
    
    with comparison_tabs[3]:
        st.subheader("Top Features Comparison")
        if 'Feature' in df1.columns and 'Feature' in df2.columns:
            features1 = df1['Feature'].value_counts().head(10).reset_index()
            features1.columns = ['Feature', f'{month1_label}']
            
            features2 = df2['Feature'].value_counts().head(10).reset_index()
            features2.columns = ['Feature', f'{month2_label}']
            
            features_comparison = features1.merge(features2, on='Feature', how='outer').fillna(0)
            features_comparison['Change'] = features_comparison[f'{month2_label}'] - features_comparison[f'{month1_label}']
            features_comparison = features_comparison.sort_values(f'{month2_label}', ascending=False).head(10)
            features_comparison.index = features_comparison.index + 1
            
            st.dataframe(features_comparison, use_container_width=True)
            
            # Bar chart comparison
            if not features_comparison.empty:
                fig = go.Figure(data=[
                    go.Bar(name=month1_label, x=features_comparison['Feature'], y=features_comparison[f'{month1_label}']),
                    go.Bar(name=month2_label, x=features_comparison['Feature'], y=features_comparison[f'{month2_label}'])
                ])
                fig.update_layout(
                    title=f"Top Features: {month1_label} vs {month2_label}",
                    barmode='group',
                    xaxis_title="Feature",
                    yaxis_title="Requests",
                    hovermode='x unified',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No feature data available")
    
    with comparison_tabs[4]:
        st.subheader("Support Tier Comparison")
        if 'Support Tier' in df1.columns and 'Support Tier' in df2.columns:
            tier1 = df1['Support Tier'].value_counts().reset_index()
            tier1.columns = ['Support Tier', f'{month1_label}']
            
            tier2 = df2['Support Tier'].value_counts().reset_index()
            tier2.columns = ['Support Tier', f'{month2_label}']
            
            tier_comparison = tier1.merge(tier2, on='Support Tier', how='outer').fillna(0)
            tier_comparison['Change'] = tier_comparison[f'{month2_label}'] - tier_comparison[f'{month1_label}']
            tier_comparison.index = tier_comparison.index + 1
            
            st.dataframe(tier_comparison, use_container_width=True)
            
            # Bar chart comparison
            if not tier_comparison.empty:
                fig = go.Figure(data=[
                    go.Bar(name=month1_label, x=tier_comparison['Support Tier'], y=tier_comparison[f'{month1_label}']),
                    go.Bar(name=month2_label, x=tier_comparison['Support Tier'], y=tier_comparison[f'{month2_label}'])
                ])
                fig.update_layout(
                    title=f"Support Tier Distribution: {month1_label} vs {month2_label}",
                    barmode='group',
                    xaxis_title="Support Tier",
                    yaxis_title="Count",
                    hovermode='x unified',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No support tier data available")

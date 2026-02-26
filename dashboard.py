import streamlit as st
import pandas as pd
from pathlib import Path
import re
from datetime import datetime
from styles import load_css
from metrics.metric1_total_questions import show_total_questions
from metrics.metric2_most_features import show_most_features
from metrics.metric3_feature_support_tier import show_feature_support_tier
from metrics.metric4_support_tier import show_support_tier
from metrics.metric5_top_sales_curiosity import show_top_sales_curiosity
from metrics.metric6_sales_support_tier import show_sales_support_tier
from metrics.metric7_week_comparison import show_week_comparison
from metrics.metric8_month_comparison import show_month_comparison

# Page configuration
st.set_page_config(
    page_title="Support Data Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS styles
load_css()

# Dashboard title with icon
st.markdown("<h1>Support Data Analytics Dashboard</h1>", unsafe_allow_html=True)

# Data source selector
data_source = st.radio(
    "Select Data Source",
    ["📁 Upload File", "🌐 Google Sheet (Public URL)"],
    horizontal=True
)

uploaded_file = None
google_sheet_url = None

if data_source == "📁 Upload File":
    # File uploader
    uploaded_file = st.file_uploader(
        "📁 Upload your Excel/CSV file",
        type=["csv", "xlsx"],
        help="Upload a CSV or Excel file containing your support data"
    )
else:
    # Google Sheet URL input
    google_sheet_url = st.text_input(
        "🔗 Enter Google Sheet URL",
        placeholder="https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit...",
        help="Paste the URL of your public Google Sheet (must be viewable by anyone with the link)"
    )
    
    # Sheet selector for multiple sheets (appears after URL is entered)
    sheet_gid = None
    if google_sheet_url:
        st.info("💡 If your Google Sheet has multiple sheets (tabs), you can specify which one to load:")
        sheet_option = st.selectbox(
            "Select Sheet",
            ["First Sheet (default)", "Enter Sheet GID manually"],
            help="Each sheet in Google Sheets has a unique GID number. You can find it in the URL when you click on a sheet tab."
        )
        
        if sheet_option == "Enter Sheet GID manually":
            sheet_gid = st.text_input(
                "Sheet GID",
                placeholder="0",
                help="The GID is in the URL when viewing a specific sheet: ...#gid=123456789. The first sheet is usually 0."
            )
            st.caption("📝 **How to find the GID:** Click on the sheet tab you want (e.g., 'February'), then look at the URL: `...#gid=123456789`. The number after `gid=` is what you need.")

if uploaded_file or google_sheet_url:
    # Robust data loader for CSV/Excel
    def load_dataframe(file):
        filename = getattr(file, "name", "uploaded")
        suffix = Path(filename).suffix.lower()

        expected_cols = {"Week", "Merchants", "Sales"}

        def clean_df(df_in: pd.DataFrame) -> pd.DataFrame:
            df_out = df_in.copy()
            # Normalize headers
            df_out.columns = df_out.columns.astype(str).str.strip()
            # Drop unnamed/empty columns
            df_out = df_out.loc[:, ~df_out.columns.str.match(r"^Unnamed", na=False)]
            # Drop fully empty rows
            df_out = df_out.dropna(how="all")
            # Convert dtypes more consistently
            with pd.option_context("future.no_silent_downcasting", True):
                df_out = df_out.convert_dtypes()
            return df_out

        if suffix == ".csv":
            df0 = pd.read_csv(file)
            return clean_df(df0)

        # Excel handling (multiple sheets, header auto-detection)
        try:
            xls = pd.ExcelFile(file, engine="openpyxl")
        except Exception:
            xls = pd.ExcelFile(file)

        best_df = None
        best_score = -1
        for sheet in xls.sheet_names:
            # First try with default header
            try:
                df_default = pd.read_excel(xls, sheet_name=sheet)
                df_default = clean_df(df_default)
            except Exception:
                df_default = pd.DataFrame()

            needs_scan = (
                df_default.empty
                or (df_default.columns.str.match(r"^Unnamed").sum() > len(df_default.columns) // 2)
                or (expected_cols.intersection(set(df_default.columns)) == set())
            )

            candidate_dfs = []
            if not df_default.empty:
                candidate_dfs.append(df_default)

            if needs_scan:
                try:
                    raw = pd.read_excel(xls, sheet_name=sheet, header=None)
                    # Scan first 15 rows to find header row containing expected columns
                    header_row = None
                    for i in range(min(15, len(raw))):
                        row_vals = raw.iloc[i].astype(str).str.strip().tolist()
                        overlap = expected_cols.intersection(set(row_vals))
                        if len(overlap) >= 2 or ("Week" in row_vals):
                            header_row = i
                            break
                    if header_row is not None:
                        df_scan = raw.iloc[header_row + 1:].copy()
                        headers = raw.iloc[header_row].astype(str).str.strip()
                        df_scan.columns = headers
                        df_scan = clean_df(df_scan)
                        if not df_scan.empty:
                            candidate_dfs.append(df_scan)
                except Exception:
                    pass

            # Score candidates: prefer those covering expected columns and having more rows
            for cdf in candidate_dfs:
                score = 0
                score += len(expected_cols.intersection(set(cdf.columns))) * 10
                score += max(0, len(cdf))
                # Penalize too few columns
                score -= 5 if cdf.shape[1] < 2 else 0
                if score > best_score:
                    best_score = score
                    best_df = cdf

        if best_df is None:
            # Final fallback: read first sheet
            df_fallback = pd.read_excel(xls, sheet_name=0)
            return clean_df(df_fallback)

        return best_df

    # Function to load data from Google Sheets
    @st.cache_data(ttl=60)  # Cache for 60 seconds
    def load_google_sheet(url, gid=None):
        try:
            # Extract the sheet ID from the URL
            match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
            if not match:
                st.error("❌ Invalid Google Sheets URL. Please check the URL and try again.")
                return None

            sheet_id = match.group(1)

            # If the user pasted a URL with a gid but left the selector on "First Sheet",
            # honor the gid from the URL instead of silently defaulting to the doc's first sheet.
            sheet_gid = gid
            if sheet_gid is None:
                gid_match = re.search(r'(?:[?&#])gid=(\d+)', url)
                if gid_match:
                    sheet_gid = gid_match.group(1)

            # Construct the CSV export URL for public sheets
            if sheet_gid:
                csv_export_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={sheet_gid}'
            else:
                csv_export_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv'

            # Try to read the data
            df = pd.read_csv(csv_export_url)

            # Clean the dataframe
            df.columns = df.columns.astype(str).str.strip()
            df = df.loc[:, ~df.columns.str.match(r"^Unnamed", na=False)]
            df = df.dropna(how="all")

            with pd.option_context("future.no_silent_downcasting", True):
                df = df.convert_dtypes()

            return df

        except Exception as e:
            st.error(f"❌ Error loading Google Sheet: {str(e)}")
            st.info("💡 Make sure the Google Sheet is set to 'Anyone with the link can view'")
            if gid:
                st.warning("⚠️ If you specified a GID, make sure it's correct. Try without the GID first to load the first sheet.")
            return None

    # Load data based on source
    if uploaded_file:
        df = load_dataframe(uploaded_file)
    else:
        df = load_google_sheet(google_sheet_url, gid=sheet_gid)
    
    if df is None:
        st.stop()
    
    # Add manual refresh button for Google Sheets
    if google_sheet_url:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("🔄 Refresh Data", key="refresh_button", help="Manually refresh data from Google Sheet"):
                st.cache_data.clear()  # Clear the cache
                st.rerun()  # Rerun the app
        with col3:
            st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
    
    # Clean column names
    df.columns = df.columns.astype(str).str.strip()
    
    # Filter out rows with empty critical columns (Merchants, Sales, Issue)
    critical_cols = ['Merchants', 'Sales', 'Issue']
    existing_critical = [col for col in critical_cols if col in df.columns]
    if existing_critical:
        # Keep rows where at least one critical column has a non-empty value
        mask = df[existing_critical].notna().any(axis=1) & (df[existing_critical].astype(str).replace('', pd.NA).notna().any(axis=1))
        df = df[mask]

    # Store the full unfiltered dataframe for Week Comparison
    df_full = df.copy()

    # Week filter (Whole Month or dynamically detected weeks)
    week_col = 'Week' if 'Week' in df.columns else df.columns[0]
    
    # Detect available weeks in the data
    available_weeks = set()
    if week_col:
        week_series = df[week_col].astype(str)
        # Extract all week numbers (handles W1, W2, Week 1, 1, etc.)
        import re as regex_module
        for val in week_series.unique():
            match = regex_module.search(r'[Ww]?(\d+)', val)
            if match:
                week_num = int(match.group(1))
                available_weeks.add(week_num)
    
    # Build dynamic week options
    week_options = [f"Week {i}" for i in sorted(available_weeks)] + ["Whole Month"]
    
    week_filter = st.sidebar.selectbox(
        "Filter by Week",
        week_options,
        help="Filter rows where the week column contains week numbers. Choose Whole Month to see all."
    )
    
    # Apply week filter only for non-comparison sections
    df_filtered = df.copy()
    if week_filter != "Whole Month" and week_col:
        key = week_filter.split()[-1]  # "1".."4"
        week_series = df_filtered[week_col].astype(str)
        week_mask = week_series.str.contains(fr"W\s*{key}", case=False, na=False) | week_series.str.fullmatch(key)
        df_filtered = df_filtered[week_mask]
    if df_filtered.empty:
        st.warning("No data for the selected week filter.")
        st.stop()
    
    st.sidebar.markdown("---")
    
    section = st.sidebar.radio(
        "Dashboard Sections:",
        [
            "📈 Overview & Metrics",
            "🔥 Feature Analysis",
            "📊 Support Tier Overview",
            "🎨 Feature & Support Tier",
            "⭐ Sales Performance",
            "👥 Sales & Support Tier",
            "⏰ Week Comparison",
            "🗓️ Month Comparison"
        ],
        key="nav_radio",
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("---")
    
    # Quick stats in sidebar
    st.sidebar.markdown(
        """
        <div style='background: white; padding: 1rem; border-radius: 10px; margin: 1rem 0; box-shadow: 0 2px 8px rgba(0,0,0,0.05);'>
            <h4 style='color: #475569; margin-bottom: 0.5rem;'>📋 Quick Stats</h4>
            <p style='color: #64748b; margin: 0.25rem 0; font-size: 0.9rem;'>
                📝 Total Questions: <strong>{}</strong>
            </p>
            <p style='color: #64748b; margin: 0.25rem 0; font-size: 0.9rem;'>
                🏢 Total Merchants: <strong>{}</strong>
            </p>
            <p style='color: #64748b; margin: 0.25rem 0; font-size: 0.9rem;'>
                👥 Total Sales: <strong>{}</strong>
            </p>
        </div>
        """.format(
            len(df_filtered),
            df_filtered['Merchants'].nunique() if 'Merchants' in df_filtered.columns else 'N/A',
            df_filtered['Sales'].nunique() if 'Sales' in df_filtered.columns else 'N/A'
        ),
        unsafe_allow_html=True
    )
    
    st.sidebar.markdown(
        "<p style='color: #94a3b8; text-align: center; font-size: 0.8rem; margin-top: 1rem;'>💡 Tip: Click on chart legends for interactive filtering</p>",
        unsafe_allow_html=True
    )
    
    # Display selected section
    if section == "📈 Overview & Metrics":
        show_total_questions(df_filtered)
    elif section == "🔥 Feature Analysis":
        show_most_features(df_filtered)
    elif section == "📊 Support Tier Overview":
        show_feature_support_tier(df_filtered)
    elif section == "🎨 Feature & Support Tier":
        show_support_tier(df_filtered)
    elif section == "⭐ Sales Performance":
        show_top_sales_curiosity(df_filtered)
    elif section == "👥 Sales & Support Tier":
        show_sales_support_tier(df_filtered)
    elif section == "⏰ Week Comparison":
        show_week_comparison(df_full)
    elif section == "🗓️ Month Comparison":
        show_month_comparison(data_source, uploaded_file, google_sheet_url)
        
else:
    # Welcome screen
    st.info(
        "👋 **Welcome to the Support Data Dashboard!** Please upload your data file to begin analysis.",
        icon="ℹ️"
    )
    
    # Feature cards in grid layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div style='background: white; padding: 1.5rem; border-radius: 12px; height: 100%; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;'>
                <h3 style='color: #1e293b; margin-bottom: 1rem;'>📊 Data Visualization</h3>
                <p style='color: #64748b;'>
                    Interactive charts with real-time filtering and detailed insights for better decision making.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style='background: white; padding: 1.5rem; border-radius: 12px; height: 100%; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;'>
                <h3 style='color: #1e293b; margin-bottom: 1rem;'>📈 Performance Metrics</h3>
                <p style='color: #64748b;'>
                    Track sales performance, support tiers, and feature requests with comprehensive analytics.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div style='background: white; padding: 1.5rem; border-radius: 12px; height: 100%; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;'>
                <h3 style='color: #1e293b; margin-bottom: 1rem;'>🎯 Interactive Analysis</h3>
                <p style='color: #64748b;'>
                    Clickable legends, hover details, and customizable views for deep data exploration.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    # Supported formats
    st.markdown("""
        <div style='background: white; padding: 1.5rem; border-radius: 12px; margin-top: 2rem; border: 1px solid #e2e8f0;'>
            <h3 style='color: #1e293b; margin-bottom: 1rem;'>📋 Supported Formats</h3>
            <div style='display: flex; gap: 1rem; align-items: center;'>
                <div style='padding: 0.5rem 1rem; background: #f1f5f9; border-radius: 6px; color: #475569;'>
                    📄 CSV Files
                </div>
                <div style='padding: 0.5rem 1rem; background: #f1f5f9; border-radius: 6px; color: #475569;'>
                    📊 Excel Files
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Add footer
st.markdown("""
    <div style='text-align: center; margin-top: 3rem; padding: 1rem; color: #94a3b8; font-size: 0.9rem;'>
        <hr style='margin-bottom: 1rem;'>
        <p>Support Data Dashboard v1.0 • Built with Streamlit</p>
    </div>
""", unsafe_allow_html=True)

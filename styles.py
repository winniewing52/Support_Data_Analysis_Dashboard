import streamlit as st

def load_css():
    """Load and apply the dashboard CSS styling"""
    st.markdown("""
        <style>
        /* Main background - Light theme */
        .main {
            background-color: #f8fafc;
            background-image: radial-gradient(#e2e8f0 1px, transparent 1px);
            background-size: 20px 20px;
        }
        
        /* Sidebar styling - Clean light theme */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
            border-right: 1px solid #e2e8f0;
        }
        
        [data-testid="stSidebar"] .css-1d391kg, 
        [data-testid="stSidebar"] .st-emotion-cache-16idsys {
            color: #1e293b;
        }
        
        /* Headers styling */
        h1 {
            color: #1e293b;
            font-size: 2.5rem !important;
            font-weight: 700 !important;
            text-align: center;
            margin-bottom: 1.5rem !important;
            padding-bottom: 1rem;
            border-bottom: 3px solid #3b82f6;
            background: linear-gradient(90deg, #3b82f6, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        h2 {
            color: #334155;
            font-weight: 600 !important;
            margin-top: 1.5rem !important;
            padding: 0.75rem 0;
            border-bottom: 2px solid #e2e8f0;
        }
        
        h3 {
            color: #475569;
            font-weight: 500 !important;
            margin-top: 1.25rem !important;
        }
        
        /* Modern metric cards with glass effect */
        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            padding: 1.25rem;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.3);
            transition: all 0.3s ease;
        }
        
        [data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(0, 0, 0, 0.12);
        }
        
        [data-testid="stMetric"] label {
            color: #64748b !important;
            font-size: 0.9rem !important;
            font-weight: 500 !important;
            letter-spacing: 0.5px;
        }
        
        [data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: #1e293b !important;
            font-size: 2rem !important;
            font-weight: 700 !important;
        }
        
        /* Dataframe styling - Clean card design */
        [data-testid="stDataFrame"] {
            background: white;
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            border: 1px solid #e2e8f0;
        }
        
        /* Info box - Modern alert */
        .stAlert {
            background: linear-gradient(135deg, #dbeafe 0%, #e0e7ff 100%) !important;
            border-radius: 12px !important;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05) !important;
            border: 1px solid #c7d2fe !important;
            border-left: 4px solid #4f46e5 !important;
        }
        
        /* Sidebar radio buttons - Modern toggle */
        [data-testid="stSidebar"] .row-widget.stRadio > div {
            background: white;
            padding: 0.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
            border: 1px solid #e2e8f0;
        }
        
        [data-testid="stSidebar"] .row-widget.stRadio label {
            color: #475569 !important;
            font-weight: 400 !important;
            padding: 0.5rem;
            border-radius: 6px;
            transition: all 0.2s ease;
        }
        
        [data-testid="stSidebar"] .row-widget.stRadio label:hover {
            background-color: #f1f5f9;
        }
        
        [data-testid="stSidebar"] .row-widget.stRadio div[role="radiogroup"] > label[data-baseweb="radio"]:first-child {
            color: #1e293b !important;
            font-weight: 500 !important;
            background-color: #f8fafc;
            border-radius: 6px;
        }
        
        /* File uploader - Clean design */
        [data-testid="stFileUploader"] {
            background: white;
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            border: 2px dashed #cbd5e1;
            transition: all 0.3s ease;
        }
        
        [data-testid="stFileUploader"]:hover {
            border-color: #3b82f6;
            box-shadow: 0 6px 25px rgba(59, 130, 246, 0.1);
        }
        
        /* Divider */
        hr {
            margin: 1.5rem 0;
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        }
        
        /* Chart containers - Clean card */
        .js-plotly-plot {
            background: white;
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            border: 1px solid #e2e8f0;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1.5rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
        }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f5f9;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #94a3b8;
        }
        
        /* Tab styling if used */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            padding: 0.75rem 1.5rem;
            background-color: #f1f5f9;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: white;
            border-bottom: 2px solid #3b82f6;
        }
        
        /* Text input styling */
        .stTextInput > div > div > input {
            border-radius: 8px;
            border: 1px solid #cbd5e1;
            transition: all 0.3s ease;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
        }
        </style>
    """, unsafe_allow_html=True)

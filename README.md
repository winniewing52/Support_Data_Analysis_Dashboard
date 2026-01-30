# 📊 Support Data Analytics Dashboard

A modern, interactive Streamlit dashboard for analyzing support data from merchants, featuring multiple metrics and visualizations to track questions, features, support tiers, and sales curiosity.

## 🌟 Features

- **Multiple Data Sources**: Upload CSV/Excel files or connect to Google Sheets
- **Modern UI**: Clean, light-themed interface with smooth animations and glass-effect cards
- **Six Key Metrics**:
  1. Total Questions & Merchants
  2. Most Features Asked by Merchant
  3. Support Tier Overview
  4. Feature Distribution by Support Tier
  5. Top Sales with Most Customer's Curiosity
  6. IT Support Tier by Sales

- **Interactive Visualizations**: Charts and tables with hover effects
- **Real-time Analysis**: Instant insights from your support data

## 📋 Requirements

- Python 3.7+
- Streamlit
- Pandas
- openpyxl (for Excel file support)

## 🚀 Installation

1. **Clone or download this repository**

2. **Install required packages**:
```bash
pip install streamlit pandas openpyxl
```

## 💻 Usage

1. **Run the dashboard**:
```bash
streamlit run dashboard.py
```

2. **Load your data**:
   - Choose between uploading a file or connecting to a Google Sheet
   - For file upload: Click "📁 Upload File" and select your CSV or Excel file
   - For Google Sheet: Select "🌐 Google Sheet" and paste the public URL

3. **Explore the metrics**:
   - Use the sidebar to navigate between different metric views
   - Interact with charts and tables to gain insights

## 📊 Data Format

Your data file should contain the following columns:

| Column Name | Description | Example |
|-------------|-------------|---------|
| `Week` | The week identifier | Week 1, Week 2, etc. |
| `Merchants` | Merchant name | Wingles, Rapoling |
| `Sales` | Sales representative name | John Doe, Jane Smith |
| `Issue` | The question or topic asked | "Appt > reminder inquiries" |
| `Feature Category` | Feature category | Appointment, Order, etc. |
| `IT Support Tier` | Support tier level | First Layer, Operation, etc. |

## 🎨 Dashboard Features

### Modern Light Theme
- Gradient headers and smooth transitions
- Custom scrollbar styling
- Responsive layout that adapts to screen size

### Navigation
- Sidebar navigation for easy metric switching
- Clear section headers and dividers
- Hover effects for better interactivity

## 🐛 Troubleshooting

### "streamlit: command not found"
- Make sure Streamlit is installed: `pip install streamlit`
- Try: `python -m streamlit run dashboard.py`

### Data not loading
- Verify your data file has the required columns
- For Google Sheets, ensure the sheet is publicly accessible
- Check that there are no completely empty rows in your data

### Excel files not working
- Install openpyxl: `pip install openpyxl`
- Try saving as CSV instead

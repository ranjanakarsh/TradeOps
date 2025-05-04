import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import os

# constants
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
DEFAULT_PAGE_SIZE = 10

# configure page
st.set_page_config(
    page_title="TradeOps",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# custom styling
st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary-color: #1a1a1a;
        --secondary-color: #2d2d2d;
        --accent-color: #00ff00;
        --text-color: #ffffff;
        --border-color: #00ff00;
    }
    
    /* Global styles */
    .stApp {
        background-color: var(--primary-color);
        color: var(--text-color);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: var(--secondary-color) !important;
        border-right: 1px solid var(--border-color);
    }
    
    /* Sidebar section headers */
    .sidebar .stMarkdown h3 {
        color: var(--accent-color) !important;
        font-family: 'Courier New', monospace !important;
        border-bottom: 1px solid var(--border-color);
        padding-bottom: 5px;
        margin-top: 1rem;
    }
    
    /* Sidebar links */
    .sidebar a {
        color: var(--accent-color) !important;
        text-decoration: none !important;
        font-family: 'Courier New', monospace !important;
    }
    
    .sidebar a:hover {
        text-decoration: underline !important;
    }
    
    /* Sidebar version info */
    .sidebar .stMarkdown p {
        color: var(--accent-color) !important;
        font-family: 'Courier New', monospace !important;
        margin: 0.5rem 0;
    }
    
    /* Title styling */
    h1 {
        color: var(--accent-color) !important;
        font-family: 'Courier New', monospace;
        border-bottom: 2px solid var(--border-color);
        padding-bottom: 10px;
    }
    
    /* Subheader styling */
    h2 {
        color: var(--accent-color) !important;
        font-family: 'Courier New', monospace;
        border-bottom: 1px solid var(--border-color);
        padding-bottom: 5px;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: var(--secondary-color) !important;
        color: var(--accent-color) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 0 !important;
        font-family: 'Courier New', monospace;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: var(--accent-color) !important;
        color: var(--primary-color) !important;
    }
    
    /* Input field styling */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        background-color: var(--secondary-color) !important;
        color: var(--accent-color) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 0 !important;
        font-family: 'Courier New', monospace;
    }
    
    /* Metric styling */
    .stMetric {
        background-color: var(--secondary-color) !important;
        border: 1px solid var(--border-color) !important;
        padding: 10px;
        margin: 5px;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background-color: var(--secondary-color) !important;
        border: 1px solid var(--border-color) !important;
    }
    
    /* Chart styling */
    .plotly-graph-div {
        background-color: var(--secondary-color) !important;
        border: 1px solid var(--border-color) !important;
        padding: 10px;
    }
    
    /* Navigation styling */
    .stRadio > div {
        background-color: var(--secondary-color) !important;
        border: 1px solid var(--border-color) !important;
        padding: 10px;
    }
    
    .stRadio > div > label {
        color: var(--accent-color) !important;
        font-family: 'Courier New', monospace;
    }
    
    /* Success/Error message styling */
    .stAlert {
        background-color: var(--secondary-color) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--accent-color) !important;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .stMetric {
            width: 100% !important;
        }
        
        .stButton > button {
            width: 100% !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def show_sidebar() -> None:
    """
    display the sidebar with navigation and credits
    """
    st.sidebar.title("TradeOps")
    
    # navigation
    st.sidebar.markdown("### Navigation")
    page = st.sidebar.radio(
        "",
        ["Dashboard", "Trade Management", "Analytics", "Logs", "Database Management"],
        label_visibility="collapsed"
    )
    
    # credits
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.markdown(
        '<div style="color: var(--accent-color); font-family: Courier New, monospace;">Created by <a href="https://github.com/ranjanakarsh" style="color: var(--accent-color);">Ranjan Akarsh</a></div>',
        unsafe_allow_html=True
    )
    
    # version info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Version")
    st.sidebar.markdown(
        '<div style="color: var(--accent-color); font-family: Courier New, monospace;">v1.0.0</div>',
        unsafe_allow_html=True
    )
    
    return page

def show_dashboard() -> None:
    """
    display the main dashboard with trading activity and asset distribution
    """
    st.title("Dashboard")
    
    try:
        # get trades data
        response = requests.get(f"{API_BASE_URL}/trades")
        if response.status_code != 200:
            st.error("Error fetching trades data")
            return
            
        trades = response.json()
        if not trades:
            st.info("No trades data available")
            return
            
        # convert to dataframe
        df = pd.DataFrame(trades)
        
        # quick stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Total Trades",
                len(df),
                f"+{len(df) % 10}%"
            )
        
        with col2:
            total_volume = df['quantity'].sum()
            st.metric(
                "Total Volume",
                f"${total_volume:,.2f}",
                f"+{total_volume % 10}%"
            )
        
        with col3:
            active_traders = df['trader'].nunique()
            st.metric(
                "Active Traders",
                active_traders,
                f"+{active_traders % 5}%"
            )
        
        # main content
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Trading Activity")
            # prepare data for trading activity chart
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            daily_trades = df.groupby(df['timestamp'].dt.date).size().reset_index(name='count')
            
            # create trading activity chart
            fig = px.line(
                daily_trades,
                x='timestamp',
                y='count',
                title='Trading Activity Over Time',
                labels={'timestamp': 'Date', 'count': 'Number of Trades'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Asset Distribution")
            # prepare data for asset distribution chart
            asset_dist = df['asset_class'].value_counts().reset_index()
            asset_dist.columns = ['asset_class', 'count']
            
            # create asset distribution chart
            fig = px.pie(
                asset_dist,
                values='count',
                names='asset_class',
                title='Asset Class Distribution'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # recent trades
        st.markdown("### Recent Trades")
        recent_trades = df.sort_values('timestamp', ascending=False).head(5)
        st.dataframe(
            recent_trades[['trade_id', 'trader', 'asset_class', 'quantity', 'price', 'timestamp']],
            use_container_width=True,
            hide_index=True
        )
        
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")

def show_trade_management() -> None:
    """
    display trade management interface
    """
    st.title("Trade Management")
    
    # tabs for different actions
    tab1, tab2 = st.tabs(["Create Trade", "View Trades"])
    
    with tab1:
        show_trade_creation_form()
    
    with tab2:
        show_trades_list()

def show_trade_creation_form() -> None:
    """
    display trade creation form
    """
    with st.form("create_trade_form"):
        st.markdown("### Create New Trade")
        
        col1, col2 = st.columns(2)
        
        with col1:
            trade_id = st.text_input("Trade ID")
            trader = st.text_input("Trader")
            asset_class = st.selectbox(
                "Asset Class",
                ["EQUITY", "FIXED_INCOME", "COMMODITY", "FOREX"]
            )
            
        with col2:
            quantity = st.number_input("Quantity", min_value=1)
            price = st.number_input("Price", min_value=0.0, format="%.2f")
            
        submitted = st.form_submit_button("Create Trade")
        
        if submitted:
            try:
                # create trade data
                trade_data = {
                    "trade_id": trade_id,
                    "trader": trader,
                    "asset_class": asset_class,
                    "quantity": quantity,
                    "price": price
                }
                
                # send request
                response = requests.post(
                    f"{API_BASE_URL}/trades",
                    json=trade_data
                )
                
                if response.status_code == 200:
                    st.success("Trade created successfully")
                else:
                    st.error(f"Error creating trade: {response.text}")
                    
            except Exception as e:
                st.error(f"Error creating trade: {str(e)}")

def show_trades_list() -> None:
    """
    display trades list with filters
    """
    # filters
    col1, col2 = st.columns(2)
    
    with col1:
        trader_filter = st.text_input("Filter by Trader", key="trade_list_trader_filter")
        
    with col2:
        asset_class_filter = st.selectbox(
            "Filter by Asset Class",
            ["ALL", "EQUITY", "FIXED_INCOME", "COMMODITY", "FOREX"],
            key="trade_list_asset_filter"
        )
    
    try:
        # build query params
        params = {}
        if trader_filter:
            params["trader"] = trader_filter
        if asset_class_filter != "ALL":
            params["asset_class"] = asset_class_filter
            
        # get trades
        response = requests.get(f"{API_BASE_URL}/trades", params=params)
        if response.status_code != 200:
            st.error("Error fetching trades")
            return
            
        trades = response.json()
        if not trades:
            st.info("No trades found")
            return
            
        # convert to dataframe
        df = pd.DataFrame(trades)
        
        # show paginated table
        col1, col2 = st.columns(2)
        
        with col1:
            page_size = st.selectbox(
                "Rows per page",
                [10, 25, 50, 100],
                index=0,
                key="trade_list_page_size"
            )
        
        with col2:
            total_pages = (len(df) + page_size - 1) // page_size
            page = st.number_input(
                "Page",
                min_value=1,
                max_value=total_pages,
                value=1,
                key="trade_list_page_number"
            )
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        st.dataframe(
            df.iloc[start_idx:end_idx],
            use_container_width=True,
            hide_index=True
        )
        
    except Exception as e:
        st.error(f"Error displaying trades: {str(e)}")

def show_analytics() -> None:
    """
    display analytics dashboard
    """
    st.title("Analytics")
    
    try:
        # get trades data
        response = requests.get(f"{API_BASE_URL}/trades")
        if response.status_code != 200:
            st.error("Error fetching trades data")
            return
            
        trades = response.json()
        if not trades:
            st.info("No trades data available")
            return
            
        # convert to dataframe
        df = pd.DataFrame(trades)
        
        # time range selector
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now() - timedelta(days=30)
            )
            
        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime.now()
            )
        
        # filter data by date range
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        mask = (df['timestamp'].dt.date >= start_date) & (df['timestamp'].dt.date <= end_date)
        filtered_df = df[mask]
        
        # metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Total Trades",
                len(filtered_df),
                f"+{len(filtered_df) % 10}%"
            )
        
        with col2:
            total_volume = filtered_df['quantity'].sum()
            st.metric(
                "Total Volume",
                f"${total_volume:,.2f}",
                f"+{total_volume % 10}%"
            )
        
        with col3:
            avg_trade_size = filtered_df['quantity'].mean()
            st.metric(
                "Average Trade Size",
                f"${avg_trade_size:,.2f}",
                f"+{avg_trade_size % 5}%"
            )
        
        # charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Trading Activity")
            # prepare data for trading activity chart
            daily_volume = filtered_df.groupby(filtered_df['timestamp'].dt.date)['quantity'].sum().reset_index()
            
            # create trading activity chart
            fig = px.line(
                daily_volume,
                x='timestamp',
                y='quantity',
                title='Daily Trading Volume',
                labels={'timestamp': 'Date', 'quantity': 'Volume'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Asset Analysis")
            # prepare data for asset analysis
            asset_stats = filtered_df.groupby('asset_class').agg({
                'quantity': ['count', 'sum', 'mean']
            }).reset_index()
            
            asset_stats.columns = ['asset_class', 'trade_count', 'total_volume', 'avg_trade_size']
            
            # create asset analysis chart
            fig = px.bar(
                asset_stats,
                x='asset_class',
                y='total_volume',
                title='Volume by Asset Class',
                labels={'asset_class': 'Asset Class', 'total_volume': 'Total Volume'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # trader performance
        st.markdown("### Trader Performance")
        # prepare data for trader performance
        trader_stats = filtered_df.groupby('trader').agg({
            'quantity': ['count', 'sum', 'mean']
        }).reset_index()
        
        trader_stats.columns = ['trader', 'trade_count', 'total_volume', 'avg_trade_size']
        
        # create trader performance chart
        fig = px.bar(
            trader_stats,
            x='trader',
            y='total_volume',
            title='Volume by Trader',
            labels={'trader': 'Trader', 'total_volume': 'Total Volume'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")

def show_logs() -> None:
    """
    display operational and reconciliation logs
    """
    st.title("Logs")
    
    # tabs for different log types
    tab1, tab2 = st.tabs(["Operational Logs", "Reconciliation Logs"])
    
    with tab1:
        try:
            response = requests.get(f"{API_BASE_URL}/logs/operational")
            if response.status_code != 200:
                st.error("Error fetching operational logs")
                return
                
            operational_logs = response.json()
            show_operational_logs(operational_logs)
            
        except Exception as e:
            st.error(f"Error loading operational logs: {str(e)}")
    
    with tab2:
        try:
            response = requests.get(f"{API_BASE_URL}/logs/reconciliation")
            if response.status_code != 200:
                st.error("Error fetching reconciliation logs")
                return
                
            reconciliation_logs = response.json()
            show_reconciliation_logs(reconciliation_logs)
            
        except Exception as e:
            st.error(f"Error loading reconciliation logs: {str(e)}")

def show_operational_logs(logs: List[Dict]) -> None:
    """
    display operational logs
    args:
        logs (List[Dict]): list of operational logs
    """
    for log in logs:
        st.markdown(f"""
            <div style="
                background-color: var(--secondary-color);
                border: 1px solid var(--border-color);
                padding: 10px;
                margin: 5px 0;
            ">
                <strong>{log['timestamp']}</strong> - {log['message']}
            </div>
        """, unsafe_allow_html=True)

def show_reconciliation_logs(logs: List[Dict]) -> None:
    """
    display reconciliation logs
    args:
        logs (List[Dict]): list of reconciliation logs
    """
    for log in logs:
        st.markdown(f"""
            <div style="
                background-color: var(--secondary-color);
                border: 1px solid var(--border-color);
                padding: 10px;
                margin: 5px 0;
            ">
                <strong>{log['run_time']}</strong> - {log['summary']}
            </div>
        """, unsafe_allow_html=True)
        
        if log.get('discrepancies'):
            try:
                discrepancies = json.loads(log['discrepancies'])
                if discrepancies:
                    st.json(discrepancies)
            except json.JSONDecodeError:
                st.warning("Could not parse discrepancies data")

def show_database_management() -> None:
    """
    display database management options
    """
    st.title("Database Management")
    
    # get database info
    try:
        response = requests.get(f"{API_BASE_URL}/database/info")
        if response.status_code != 200:
            st.error("Error fetching database info")
            return
            
        db_info = response.json()
        
        # display database statistics
        st.markdown("### Database Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Total Trades",
                db_info['trades_count']
            )
        
        with col2:
            st.metric(
                "Operational Logs",
                db_info['operational_logs_count']
            )
        
        with col3:
            st.metric(
                "Reconciliation Logs",
                db_info['reconciliation_logs_count']
            )
        
        # database actions
        st.markdown("### Database Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Reset Database", key="reset_db_button"):
                try:
                    response = requests.post(f"{API_BASE_URL}/database/reset")
                    if response.status_code == 200:
                        st.success("Database reset successfully")
                    else:
                        st.error(f"Error resetting database: {response.text}")
                except Exception as e:
                    st.error(f"Error resetting database: {str(e)}")
                    
        with col2:
            if st.button("Initialize with Sample Data", key="init_db_button"):
                try:
                    response = requests.post(f"{API_BASE_URL}/database/initialize")
                    if response.status_code == 200:
                        st.success("Database initialized with sample data")
                    else:
                        st.error(f"Error initializing database: {response.text}")
                except Exception as e:
                    st.error(f"Error initializing database: {str(e)}")
        
    except Exception as e:
        st.error(f"Error loading database info: {str(e)}")

def main() -> None:
    """
    main application entry point
    """
    # show sidebar and get current page
    page = show_sidebar()
    
    # show appropriate page content
    if page == "Dashboard":
        show_dashboard()
    elif page == "Trade Management":
        show_trade_management()
    elif page == "Analytics":
        show_analytics()
    elif page == "Logs":
        show_logs()
    elif page == "Database Management":
        show_database_management()

if __name__ == "__main__":
    main() 
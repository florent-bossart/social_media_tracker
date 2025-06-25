"""
Database service module for the Japanese Music Trends Dashboard.
Handles all database connections and core data fetching functionality.
"""

import pandas as pd
import streamlit as st
from config_online import get_database_engine
import warnings

warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy connectable")

@st.cache_resource
def get_engine():
    """Get cached database engine connection using online config."""
    return get_database_engine()

def fetch_data(query, params=None):
    """
    Execute SQL query and return results as DataFrame.
    Returns empty DataFrame if database is not available (for demo/Docker deployments).

    Args:
        query (str): SQL query to execute
        params (list, optional): Parameters for the query

    Returns:
        pd.DataFrame: Query results or empty DataFrame if DB unavailable
    """
    try:
        engine = get_engine()
        actual_params = [] if params is None else params
        return pd.read_sql_query(query, engine, params=actual_params)
    except Exception as e:
        # Database not available - return empty DataFrame for demo mode
        # This allows the dashboard to run without database in Docker/demo environments
        print(f"Database unavailable: {str(e)}")  # Log to console instead of UI
        return pd.DataFrame()

"""
Database service module for the Japanese Music Trends Dashboard - ONLINE VERSION.
Handles all database connections using Supabase for online deployment.
"""

import pandas as pd
import streamlit as st
import warnings
from config_online import get_database_engine

warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy connectable")

@st.cache_resource
def get_engine():
    """Get cached database engine connection for online deployment."""
    return get_database_engine()

def fetch_data(query, params=None):
    """
    Execute SQL query and return results as DataFrame.

    Args:
        query (str): SQL query to execute
        params (list, optional): Parameters for the query

    Returns:
        pd.DataFrame: Query results
    """
    engine = get_engine()
    actual_params = [] if params is None else params
    return pd.read_sql_query(query, engine, params=actual_params)

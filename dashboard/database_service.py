"""
Database service module for the Japanese Music Trends Dashboard.
Handles all database connections and core data fetching functionality.
"""

import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from dotenv import load_dotenv
import warnings

warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy connectable")

# Load environment variables
load_dotenv()

# Database connection parameters
PG_USER = os.getenv("WAREHOUSE_USER")
PG_PW = os.getenv("WAREHOUSE_PASSWORD")
PG_HOST = os.getenv("WAREHOUSE_HOST")
PG_PORT = os.getenv("WAREHOUSE_PORT")
PG_DB = os.getenv("WAREHOUSE_DB")

DATABASE_URL = f"postgresql+psycopg2://{PG_USER}:{PG_PW}@{PG_HOST}:{PG_PORT}/{PG_DB}"

@st.cache_resource
def get_engine():
    """Get cached database engine connection."""
    return create_engine(DATABASE_URL)

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

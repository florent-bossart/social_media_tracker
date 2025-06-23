#!/usr/bin/env python3
"""
Online Configuration for Streamlit Dashboard using Supabase
This configuration is specifically for the online deployment.
"""

import os
import streamlit as st
from sqlalchemy import create_engine

def get_database_config():
    """Get database configuration for online deployment."""
    
    # For Streamlit Cloud, we'll use st.secrets
    # For local testing, we'll try environment variables first
    
    try:
        # Try Streamlit secrets first (for Streamlit Cloud deployment)
        if hasattr(st, 'secrets') and 'database' in st.secrets:
            return {
                'host': st.secrets.database.host,
                'port': int(st.secrets.database.port),
                'database': st.secrets.database.database,
                'username': st.secrets.database.username,
                'password': st.secrets.database.password
            }
    except:
        pass
    
    # Fallback to environment variables (for local testing)
    online_db_host = os.getenv('ONLINE_DB_HOST', '')
    online_db_password = os.getenv('ONLINE_DB_PASSWORD', '')
    online_db_name = os.getenv('ONLINE_DB_NAME', 'postgres')
    online_db_user = os.getenv('ONLINE_DB_USER', 'postgres')
    online_db_port = int(os.getenv('ONLINE_DB_PORT', 5432))
    
    if online_db_host and online_db_password:
        return {
            'host': online_db_host,
            'port': online_db_port,
            'database': online_db_name,
            'username': online_db_user,
            'password': online_db_password
        }
    
    # If no configuration found, raise an error
    raise ValueError("No database configuration found. Please set up Streamlit secrets or environment variables.")

def get_database_engine():
    """Create and return a database engine for the online deployment."""
    config = get_database_config()
    
    # Create the connection string
    connection_string = f"postgresql+psycopg2://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
    
    # Create the engine
    engine = create_engine(
        connection_string,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,    # Recycle connections after 5 minutes
        connect_args={
            "sslmode": "require",  # Supabase requires SSL
            "connect_timeout": 30
        }
    )
    
    return engine

def test_database_connection():
    """Test the database connection."""
    try:
        engine = get_database_engine()
        with engine.connect() as conn:
            result = conn.execute("SELECT 1 as test")
            return True, "Connection successful!"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"

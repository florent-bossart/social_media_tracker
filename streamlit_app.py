#!/usr/bin/env python3
"""
Streamlit Cloud Entry Point for Social Media Tracker Dashboard

This file serves as the entry point for Streamlit Cloud deployment.
It imports and runs the online dashboard version.
"""

import sys
import os

# Get the absolute path to the dashboard_online directory
dashboard_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dashboard_online')

# Add the dashboard_online directory to the Python path at the beginning
sys.path.insert(0, dashboard_dir)

# Change working directory to dashboard_online to help with relative imports
original_cwd = os.getcwd()
os.chdir(dashboard_dir)

try:
    # Import the main dashboard - this will execute the dashboard code
    import main_dashboard
except ImportError as e:
    import streamlit as st
    st.error(f"Failed to import dashboard: {e}")
    st.error("Make sure all required dependencies are installed.")
    st.error(f"Dashboard directory: {dashboard_dir}")
    st.error(f"Current working directory: {os.getcwd()}")
    st.error(f"Python path: {sys.path[:3]}...")
    st.stop()
except Exception as e:
    import streamlit as st
    st.error(f"Error running dashboard: {e}")
    st.error("Please check the logs for more details.")
    st.stop()
finally:
    # Restore original working directory
    os.chdir(original_cwd)

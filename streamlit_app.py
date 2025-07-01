# streamlit_app.py

"""
Streamlit Entry Point for Japanese Music Trends Dashboard
Hugging face space version.
"""

import os
import sys
import streamlit as st

# Setup Streamlit early
st.set_page_config(
    page_title="🎌 Japanese Music Trends Dashboard",
    page_icon="🎵",
    layout="wide"
)

# Add dashboard directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dashboard_online'))

# Optional Debug Sidebar
if st.sidebar.checkbox("🔍 Show Debug Info", value=False):
    st.sidebar.write(f"**Python Path:** {sys.path[:2]}")
    st.sidebar.write(f"**Working Dir:** {os.getcwd()}")
    try:
        import dashboard_online.main_dashboard
        st.sidebar.success("✅ main_dashboard import successful")
    except Exception as e:
        st.sidebar.error(f"❌ Import failed: {e}")

# Attempt to run the dashboard
try:
    from dashboard_online.main_dashboard import run_dashboard
    run_dashboard()

except Exception as e:
    st.error("❌ Failed to run the dashboard.")
    st.code(str(e))
    st.warning("Check your imports, paths, or database config.")

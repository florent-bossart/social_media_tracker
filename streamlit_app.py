#!/usr/bin/env python3
"""
Streamlit Cloud Entry Point for Social Media Tracker Dashboard

This file serves as the entry point for Streamlit Cloud deployment.
It imports and runs the online dashboard version.
"""

import sys
import os

# Add the dashboard_online directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard_online'))

# Import and run the main dashboard
from main_dashboard import main

if __name__ == "__main__":
    main()

"""
Main Dashboard for Japanese Music Trends.
Orchestrates all components and handles the main application flow.
IMPROVED VERSION with consolidated pages and standardized components.
"""

import streamlit as st
import pandas as pd
import traceback
from data_manager import DataManager
from ui_library import (
    apply_global_styles, create_dashboard_header, Navigation,
    StandardComponents, UITheme
)
from artist_analytics_hub import artist_analytics_hub_page
from ai_intelligence_center import ai_intelligence_center_page
from enhanced_genre_analysis import enhanced_genre_analysis_page
from dashboard_pages import (
    overview_page, wordcloud_page, platform_insights_page, get_lucky_page
)

# Configure Streamlit page
st.set_page_config(
    page_title="🎌 Japanese Music Trends Dashboard",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global styling and create header
apply_global_styles()
create_dashboard_header()

# Initialize session state for consistent user experience
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.last_refresh = pd.Timestamp.now()

# Create consolidated sidebar navigation
page = Navigation.create_sidebar_nav()

# Simplified debug info in sidebar (no rerun-triggering elements)
with st.sidebar.expander("🔍 Debug Info", expanded=False):
    st.write(f"Current page: {page}")
    st.write(f"Data loaded: {'data_loaded' in st.session_state}")
    if 'dashboard_data' in st.session_state:
        st.write("Data keys:", list(st.session_state.dashboard_data.keys()))
    
    # Non-interactive refresh instructions
    st.info("To refresh data: Use browser refresh (F5) or clear cache below")

# Simplified cache management
if st.sidebar.button("�️ Clear Cache & Refresh"):
    # Clear cache and session state
    st.cache_data.clear()
    for key in list(st.session_state.keys()):
        if key not in ['initialized']:  # Keep initialization state
            del st.session_state[key]
    st.rerun()

# Load data using centralized DataManager
@st.cache_data
def load_consolidated_data():
    """Load all required data with improved error handling and consistency"""
    try:
        data = {}
        
        # Core data for overview and genre analysis
        data['stats'] = DataManager.get_overall_stats() or {}
        data['artist_data'] = DataManager.get_artist_trends()
        if data['artist_data'].empty:
            data['artist_data'] = pd.DataFrame(columns=['artist_name', 'mention_count', 'sentiment_score'])
        
        data['genre_data'] = DataManager.get_genre_trends()
        if data['genre_data'].empty:
            data['genre_data'] = pd.DataFrame(columns=['genre_name', 'mention_count', 'sentiment_score'])
            
        data['genre_artist_diversity_data'] = DataManager.get_genre_artist_diversity()
        data['artists_without_genre_count'] = DataManager.get_artists_without_genre_count() or 0
        data['platform_data'] = DataManager.get_platform_data()
        data['temporal_data'] = DataManager.get_temporal_data()
        data['wordcloud_data'] = DataManager.get_wordcloud_data()
        data['video_context_data'] = DataManager.get_video_context_data()
        
        return data

    except Exception as e:
        st.error(f"Error loading dashboard data: {str(e)}")
        
        # Return minimal fallback data to prevent blank screen
        return {
            'stats': {},
            'artist_data': pd.DataFrame(columns=['artist_name', 'mention_count', 'sentiment_score']),
            'genre_data': pd.DataFrame(columns=['genre_name', 'mention_count', 'sentiment_score']),
            'genre_artist_diversity_data': pd.DataFrame(),
            'artists_without_genre_count': 0,
            'platform_data': pd.DataFrame(),
            'temporal_data': pd.DataFrame(),
            'wordcloud_data': pd.DataFrame(),
            'video_context_data': pd.DataFrame()
        }

# Load data with progress indicator outside cache
if 'data_loaded' not in st.session_state:
    with st.spinner("Loading dashboard data..."):
        st.session_state.dashboard_data = load_consolidated_data()
        st.session_state.data_loaded = True

data = st.session_state.dashboard_data

# Route to appropriate consolidated page
try:
    # Force content to display - add immediate content for each page
    st.markdown(f"# Currently viewing: {page}")
    
    if page == "🏠 Overview":
        overview_page(
            data['stats'],
            data['artist_data'],
            data['temporal_data']
        )

    elif page == "🎤 Artist Analytics Hub":
        st.markdown("Loading Artist Analytics Hub...")
        artist_analytics_hub_page()

    elif page == "🎶 Genre Analysis":
        st.markdown("Loading Genre Analysis...")
        enhanced_genre_analysis_page()

    elif page == "☁️ Word Cloud":
        st.markdown("Loading Word Cloud...")
        wordcloud_page(data['wordcloud_data'])

    elif page == "📱 Platform Insights":
        st.markdown("Loading Platform Insights...")
        platform_insights_page(data['platform_data'], data['video_context_data'])

    elif page == "🤖 AI Intelligence Center":
        st.markdown("Loading AI Intelligence Center...")
        ai_intelligence_center_page()

    elif page == "🎲 Get Lucky":
        st.markdown("Loading Get Lucky...")
        get_lucky_page()

    else:
        st.error(f"Unknown page: {page}")

except Exception as e:
    st.error(f"Error rendering page '{page}': {str(e)}")
    st.code(traceback.format_exc())
    
    # Show a minimal fallback
    st.subheader(f"⚠️ {page} - Service Temporarily Unavailable")
    st.info("There was an issue loading this page. Please try refreshing or contact support if the issue persists.")
    
    # Show available data for debugging
    if st.checkbox("Show debug information"):
        st.json({
            "page": page,
            "error": str(e),
            "data_keys": list(data.keys()) if data else []
        })

# Add footer
Navigation.page_footer()

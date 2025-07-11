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

# Load data using centralized DataManager
@st.cache_data
def load_consolidated_data():
    """Load all required data with improved error handling and consistency"""
    try:
        with st.spinner("Loading dashboard data..."):
            data = {}

            # Core data for overview and genre analysis
            data['stats'] = DataManager.get_overall_stats()
            data['artist_data'] = DataManager.get_artist_trends()
            data['genre_data'] = DataManager.get_genre_trends()
            data['genre_artist_diversity_data'] = DataManager.get_genre_artist_diversity()
            data['artists_without_genre_count'] = DataManager.get_artists_without_genre_count()
            data['platform_data'] = DataManager.get_platform_data()
            data['temporal_data'] = DataManager.get_temporal_data()
            data['wordcloud_data'] = DataManager.get_wordcloud_data()

            # Video context for platform insights
            data['video_context_data'] = DataManager.get_video_context_data()

            return data

    except Exception as e:
        st.error(f"Error loading dashboard data: {str(e)}")
        StandardComponents.error_display(
            f"Data loading failed: {str(e)}",
            error_type="error"
        )
        # Return empty data structure to prevent crashes
        return {
            'stats': {},
            'artist_data': pd.DataFrame(),
            'genre_data': pd.DataFrame(),
            'genre_artist_diversity_data': pd.DataFrame(),
            'artists_without_genre_count': 0,
            'platform_data': pd.DataFrame(),
            'temporal_data': pd.DataFrame(),
            'wordcloud_data': pd.DataFrame(),
            'video_context_data': pd.DataFrame()
        }

# Load consolidated data
data = load_consolidated_data()

# Route to appropriate consolidated page
if page == "🏠 Overview":
    overview_page(
        data['stats'],
        data['artist_data'],
        data['temporal_data']
    )

elif page == "🎤 Artist Analytics Hub":
    artist_analytics_hub_page()

elif page == "🎶 Genre Analysis":
    enhanced_genre_analysis_page()

elif page == "☁️ Word Cloud":
    wordcloud_page(data['wordcloud_data'])

elif page == "📱 Platform Insights":
    platform_insights_page(data['platform_data'], data['video_context_data'])

elif page == "🤖 AI Intelligence Center":
    ai_intelligence_center_page()

elif page == "🎲 Get Lucky":
    get_lucky_page()

# Add footer
Navigation.page_footer()

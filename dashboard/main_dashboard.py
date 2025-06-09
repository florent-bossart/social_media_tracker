"""
Main Dashboard for Japanese Music Trends.
Orchestrates all components and handles the main application flow.
"""

import streamlit as st
import pandas as pd
import traceback
from data_queries import (
    get_artist_trends, get_genre_trends, get_platform_data,
    get_temporal_data, get_wordcloud_data, get_overall_stats,
    get_trend_summary_data, get_insights_summary_data,
    get_genre_artist_diversity, get_artists_without_genre_count,
    get_artist_sentiment_data, decode_artist_names, decode_genre_names,
    decode_text_fields
)
from ui_components import (
    apply_custom_css, create_header, create_sidebar, 
    initialize_session_state
)
from dashboard_pages import (
    overview_page, artist_trends_page, genre_analysis_page,
    wordcloud_page, platform_insights_page, sentiment_deep_dive_page,
    ai_trend_summary_page, ai_insights_page
)

# Configure Streamlit page
st.set_page_config(
    page_title="🎌 Japanese Music Trends Dashboard",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling and create header
apply_custom_css()
create_header()

# Initialize session state
initialize_session_state()

# Create sidebar navigation
page = create_sidebar()

# Load data using DBT models
@st.cache_data
def load_all_data():
    """Load all required data with error handling"""
    try:
        data = {}
        
        # Load main data
        data['artist_data'] = decode_artist_names(get_artist_trends())
        data['genre_data'] = get_genre_trends()
        data['genre_artist_diversity_data'] = get_genre_artist_diversity()
        data['artists_without_genre_count'] = get_artists_without_genre_count()
        data['platform_data'] = get_platform_data()
        data['temporal_data'] = get_temporal_data()
        data['wordcloud_data'] = get_wordcloud_data()
        data['artist_sentiment_data'] = decode_artist_names(get_artist_sentiment_data())

        # Load overall stats
        overall_stats_df = get_overall_stats()
        if overall_stats_df.empty:
            st.error("Error loading overall statistics: No data returned.")
            data['stats'] = pd.Series({
                'total_extractions': 0, 'avg_sentiment': 0.0,
                'unique_artists': 0, 'positive_count': 0,
                'total_sentiment_count': 0
            })
        else:
            data['stats'] = overall_stats_df.iloc[0]

        # Load summary data
        data['trend_summary_data'] = get_trend_summary_data()
        data['insights_summary_data'] = get_insights_summary_data()

        # Validate and process trend summary data
        if data['trend_summary_data'] is not None:
            if not isinstance(data['trend_summary_data'], dict):
                st.warning(f"Trend summary data has unexpected format. Got {type(data['trend_summary_data'])}, expected dict.")
                data['trend_summary_data'] = None
            else:
                for key, value in data['trend_summary_data'].items():
                    if not isinstance(value, pd.DataFrame):
                        st.warning(f"Trend summary data[{key}] has unexpected format. Got {type(value)}, expected DataFrame.")
                        data['trend_summary_data'][key] = pd.DataFrame()
                    else:
                        # Apply URL decoding where appropriate
                        if key == 'artists':
                            data['trend_summary_data'][key] = decode_artist_names(value)
                        elif key == 'genres':
                            data['trend_summary_data'][key] = decode_genre_names(value)

        # Validate and process insights summary data
        if data['insights_summary_data'] is not None:
            if not isinstance(data['insights_summary_data'], dict):
                st.warning(f"Insights summary data has unexpected format. Got {type(data['insights_summary_data'])}, expected dict.")
                data['insights_summary_data'] = None
            else:
                for key, value in data['insights_summary_data'].items():
                    if not isinstance(value, pd.DataFrame):
                        st.warning(f"Insights summary data[{key}] has unexpected format. Got {type(value)}, expected DataFrame.")
                        data['insights_summary_data'][key] = pd.DataFrame()
                    else:
                        # Apply URL decoding where appropriate
                        if key == 'artist_insights':
                            data['insights_summary_data'][key] = decode_artist_names(value)
                        elif key == 'overview':
                            data['insights_summary_data'][key] = decode_text_fields(value, ['executive_summary'])

        return data

    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.text("Full Traceback:")
        st.text(traceback.format_exc())
        st.stop()

# Load all data
data = load_all_data()

# Route to appropriate page
if page == "🏠 Overview":
    overview_page(
        data['stats'], 
        data['artist_data'], 
        data['temporal_data'], 
        data['trend_summary_data']
    )

elif page == "🎤 Artist Trends":
    artist_trends_page(
        data['artist_data'], 
        data['platform_data']
    )

elif page == "🎶 Genre Analysis":
    genre_analysis_page(
        data['genre_data'], 
        data['genre_artist_diversity_data'], 
        data['artists_without_genre_count']
    )

elif page == "☁️ Word Cloud":
    wordcloud_page(data['wordcloud_data'])

elif page == "📱 Platform Insights":
    platform_insights_page(data['platform_data'])

elif page == "💭 Sentiment Deep Dive":
    sentiment_deep_dive_page(data['artist_sentiment_data'])

elif page == "📈 AI Trend Summary":
    ai_trend_summary_page(data['trend_summary_data'])

elif page == "🔍 AI Insights":
    ai_insights_page(data['insights_summary_data'])

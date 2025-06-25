"""
UI Components module for the Japanese Music Trends Dashboard.
Contains Streamlit styling, layout components, and reusable UI elements.
"""

import streamlit as st
import pandas as pd
from data_manager import DataManager

def apply_custom_css():
    """Apply custom CSS styling for Japanese aesthetic"""
    st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-card {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #ff6b6b;
        }
        .sidebar .sidebar-content {
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        }
        .trend-positive { color: #28a745; }
        .trend-negative { color: #dc3545; }
        .trend-neutral { color: #6c757d; }
    </style>
    """, unsafe_allow_html=True)

def create_header():
    """Create the main dashboard header"""
    st.markdown(
        '<div class="main-header">'
        '<h1>🎌 Japanese Music Trends Dashboard</h1>'
        '<p>Social Media Analytics for J-Pop, City Pop, Anime Music & More</p>'
        '<p><strong>🚀 Powered by DBT Models</strong></p>'
        '</div>',
        unsafe_allow_html=True
    )

def create_sidebar():
    """Create and return sidebar navigation"""
    st.sidebar.title("🎵 Navigation")
    return st.sidebar.radio("Choose a category", [
        "🏠 Overview",
        "🎤 Artist Trends",
        "🎶 Genre Analysis",
        "☁️ Word Cloud",
        "📱 Platform Insights",
        "💭 Sentiment Deep Dive",
        "📈 AI Trend Summary",
        "🔍 AI Insights",
        "🔗 Content Discovery",
        "👥 Author Influence",
        "🎬 Video Context"
    ])

def display_metrics_row(stats):
    """Display a row of key metrics"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_mentions = DataManager.safe_convert_numeric(stats.get('total_extractions', 0)) if stats and 'total_extractions' in stats else 0
        st.metric("Total Extractions", f"{total_mentions:,}")

    with col2:
        avg_sentiment = float(stats.get('avg_sentiment', 5.0)) if stats and 'avg_sentiment' in stats else 5.0
        st.metric("Average Sentiment", f"{avg_sentiment:.1f}/10")

    with col3:
        unique_artists = DataManager.safe_convert_numeric(stats.get('unique_artists', 0)) if stats and 'unique_artists' in stats else 0
        st.metric("Unique Artists", unique_artists)

    with col4:
        if stats and 'total_sentiment_count' in stats and 'positive_count' in stats:
            total_sentiment_count = DataManager.safe_convert_numeric(stats.get('total_sentiment_count', 0))
            positive_count = DataManager.safe_convert_numeric(stats.get('positive_count', 0))
            if total_sentiment_count > 0:
                positive_pct = (positive_count / total_sentiment_count) * 100
                st.metric("Positive Sentiment", f"{positive_pct:.1f}%")
            else:
                st.metric("Positive Sentiment", "N/A")
        else:
            st.metric("Positive Sentiment", "N/A")

def display_top_artists_sidebar(artist_data):
    """Display top trending artists in sidebar format"""
    st.subheader("🔥 Top Trending Artists")
    if not artist_data.empty:
        for i, (_, artist) in enumerate(artist_data.head(5).iterrows()):
            sentiment_color = "trend-positive" if artist['sentiment_score'] > 6.5 else "trend-neutral"
            st.markdown(f"""
            <div class="metric-card">
                <strong>{i+1}. {artist['artist_name']}</strong><br>
                <span class="{sentiment_color}">Sentiment: {artist['sentiment_score']:.1f}/10</span><br>
                <small>Mentions: {artist['mention_count']} | Trend: {artist['trend_strength']:.2f}</small>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("No artist trends data available")

def display_temporal_summary(temporal_data):
    """Display temporal analysis summary metrics"""
    if temporal_data.empty:
        st.info("No temporal data available")
        return

    st.subheader("📈 Temporal Analysis Overview")

    # Calculate summary metrics
    avg_sentiment_shift = temporal_data['sentiment_shift'].mean()
    time_periods = len(temporal_data)
    high_engagement_days = len(temporal_data[temporal_data['engagement_pattern'] == 'high'])

    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Avg Sentiment Shift", f"{avg_sentiment_shift:.3f}")
    with col2:
        st.metric("Time Periods", time_periods)
    with col3:
        st.metric("High Engagement Days", high_engagement_days)
    with col4:
        total_data_points = temporal_data['data_points'].sum()
        st.metric("Total Data Points", f"{total_data_points:,}")

    # Sentiment trend interpretation
    st.subheader("📊 Sentiment Trend Status")
    if avg_sentiment_shift > 0.1:
        sentiment_status = "📈 Positive trend (sentiment improving)"
        status_color = "green"
    elif avg_sentiment_shift < -0.1:
        sentiment_status = "📉 Negative trend (sentiment declining)"
        status_color = "red"
    else:
        sentiment_status = "📊 Stable trend (sentiment steady)"
        status_color = "blue"

    st.markdown(f"""
    <div class="metric-card">
        <h4>Current Trend</h4>
        <p style="color: {status_color};">
            {sentiment_status}
        </p>
        <p><small>Based on {time_periods} time periods analyzed</small></p>
    </div>
    """, unsafe_allow_html=True)

def display_trend_summary_overview(trend_summary_data):
    """Display trend summary overview section"""
    st.subheader("📊 Trend Summary Overview")
    if trend_summary_data and 'overview' in trend_summary_data and not trend_summary_data['overview'].empty:
        overview = trend_summary_data['overview'].iloc[0]

        # Show analysis metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            # Convert timestamp to string safely
            analysis_date = str(overview['analysis_timestamp'])[:10] if pd.notna(overview['analysis_timestamp']) else "N/A"
            st.metric("Analysis Date", analysis_date)
        with col2:
            total_artists = DataManager.safe_convert_numeric(overview['total_artists_analyzed'])
            st.metric("Artists Analyzed", f"{total_artists:,}")
        with col3:
            total_genres = DataManager.safe_convert_numeric(overview['total_genres_analyzed'])
            st.metric("Genres Analyzed", f"{total_genres:,}")
        with col4:
            time_periods = DataManager.safe_convert_numeric(overview['time_periods_analyzed'])
            st.metric("Time Periods", time_periods)

        # Show trending artists count
        if 'artists' in trend_summary_data and not trend_summary_data['artists'].empty:
            artists_count = len(trend_summary_data['artists'])
            st.metric("Top Trending Artists", artists_count)

        # Show analysis settings
        st.markdown("#### Analysis Configuration")
        st.markdown(f"- **Minimum mentions for trend:** {overview['min_mentions_for_trend']}")
        st.markdown(f"- **Positive sentiment threshold:** {overview['positive_sentiment_threshold']}")
        st.markdown(f"- **Data source:** {overview['source_file']}")
    else:
        st.info("No trend summary data available")

def display_artist_details(artist_info):
    """Display detailed information for a selected artist"""
    if not artist_info:
        st.warning("No artist information available")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        mention_count = DataManager.safe_convert_numeric(artist_info.get('mention_count', 0))
        st.metric("Total Mentions", mention_count)
    with col2:
        sentiment_score = float(artist_info.get('sentiment_score', 5.0)) if artist_info.get('sentiment_score') is not None else 5.0
        st.metric("Sentiment Score", f"{sentiment_score:.1f}/10")
    with col3:
        trend_strength = float(artist_info.get('trend_strength', 0.0)) if artist_info.get('trend_strength') is not None else 0.0
        st.metric("Trend Strength", f"{trend_strength:.2f}")

def create_error_message(message, error_type="error"):
    """Create a formatted error message"""
    if error_type == "warning":
        st.warning(message)
    elif error_type == "info":
        st.info(message)
    else:
        st.error(message)

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'artist_search' not in st.session_state:
        st.session_state.artist_search = ""

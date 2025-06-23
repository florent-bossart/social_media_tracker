"""
Streamlit Cloud Optimized Version - Ultra Stable Dashboard
Minimal version designed specifically for share.streamlit.io limitations
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# Add the dashboard_online directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard_online'))

# Try to import data manager, fall back to dummy data if it fails
try:
    from data_manager import DataManager
    USE_REAL_DATA = True
except ImportError:
    USE_REAL_DATA = False
    st.error("Could not connect to database. Using demo data.")

# Configure page - minimal settings for Streamlit Cloud
st.set_page_config(
    page_title="🎌 Japanese Music Trends",
    page_icon="🎵",
    layout="wide"
)

# Minimal styling
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
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🎌 Japanese Music Trends Dashboard</h1>
    <p>Social Media Analytics for Japanese Music Community</p>
</div>
""", unsafe_allow_html=True)

# Ultra-simple navigation - no session state complexity
page = st.sidebar.selectbox(
    "📍 Navigate:",
    ["🏠 Dashboard", "📊 Analytics", "🎤 Artists", "ℹ️ About"]
)

# Dummy data for fallback
@st.cache_data
def get_dummy_data():
    """Provide dummy data if database connection fails"""
    artists = pd.DataFrame({
        'artist_name': ['Yoasobi', 'Babymetal', 'Ado', 'King Gnu', 'Official髭男dism'],
        'mention_count': [1250, 980, 875, 720, 650],
        'sentiment_score': [8.5, 7.8, 8.2, 7.5, 8.0],
        'platform_count': [2, 2, 2, 2, 2]
    })
    
    genres = pd.DataFrame({
        'genre': ['J-Pop', 'J-Rock', 'Metal', 'Alternative', 'Electronic'],
        'mention_count': [2500, 1800, 980, 750, 600],
        'sentiment_score': [8.2, 7.8, 7.5, 7.9, 8.1]
    })
    
    return artists, genres

# Load data with error handling
@st.cache_data(ttl=600)
def load_data():
    """Load data with fallback to dummy data"""
    try:
        if USE_REAL_DATA:
            artists = DataManager.get_artist_trends()
            genres = DataManager.get_genre_trends()
            
            if artists.empty or genres.empty:
                return get_dummy_data()
            return artists, genres
        else:
            return get_dummy_data()
    except Exception as e:
        st.warning(f"Database connection issue: {str(e)}")
        return get_dummy_data()

# Load data
try:
    with st.spinner("Loading data..."):
        artists_data, genres_data = load_data()
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    artists_data, genres_data = get_dummy_data()

# Page content based on selection
if page == "🏠 Dashboard":
    st.header("🌟 Overview")
    
    # Basic metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Artists", len(artists_data))
    with col2:
        st.metric("Total Mentions", f"{artists_data['mention_count'].sum():,}")
    with col3:
        st.metric("Avg Sentiment", f"{artists_data['sentiment_score'].mean():.1f}/10")
    with col4:
        st.metric("Genres", len(genres_data))
    
    # Simple chart
    st.subheader("🎤 Top Artists by Mentions")
    fig = px.bar(
        artists_data.head(10),
        x='mention_count',
        y='artist_name',
        orientation='h',
        color='sentiment_score',
        color_continuous_scale='RdYlGn',
        title="Top 10 Artists"
    )
    fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

elif page == "📊 Analytics":
    st.header("📊 Genre Analysis")
    
    # Genre metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Genres", len(genres_data))
    with col2:
        st.metric("Most Popular", genres_data.loc[genres_data['mention_count'].idxmax(), 'genre'])
    
    # Genre chart
    fig = px.bar(
        genres_data,
        x='genre',
        y='mention_count',
        color='sentiment_score',
        color_continuous_scale='RdYlGn',
        title="Genre Popularity"
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

elif page == "🎤 Artists":
    st.header("🎤 Artist Details")
    
    # Artist selection
    selected_artist = st.selectbox(
        "Choose an artist:",
        artists_data['artist_name'].tolist()
    )
    
    if selected_artist:
        artist_info = artists_data[artists_data['artist_name'] == selected_artist].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Mentions", f"{artist_info['mention_count']:,}")
        with col2:
            st.metric("Sentiment", f"{artist_info['sentiment_score']:.1f}/10")
        with col3:
            st.metric("Platforms", artist_info['platform_count'])
        
        # Artist data table
        st.subheader("📋 All Artists")
        st.dataframe(artists_data, use_container_width=True)

else:  # About page
    st.header("ℹ️ About")
    st.markdown("""
    ## 🎌 Japanese Music Trends Dashboard
    
    This dashboard analyzes Japanese music discussions across social media platforms.
    
    **Data Sources:**
    - Reddit music communities
    - YouTube music videos and comments
    - Social media sentiment analysis
    
    **Features:**
    - Real-time trend tracking
    - Sentiment analysis
    - Artist popularity metrics
    - Genre analysis
    
    **Technical Stack:**
    - Streamlit for dashboard
    - PostgreSQL/Supabase for data
    - Plotly for visualizations
    - Python for data processing
    
    ---
    
    **Note:** This is a simplified version optimized for Streamlit Cloud.
    For the full-featured dashboard with advanced analytics, please use the local deployment.
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "🎵 Japanese Music Trends Dashboard | Optimized for Streamlit Cloud"
    "</div>",
    unsafe_allow_html=True
)

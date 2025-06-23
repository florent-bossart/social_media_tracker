import streamlit as st
import pandas as pd
import os
import sqlalchemy
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import datetime
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import BytesIO
import warnings
import numpy as np
import json
from urllib.parse import unquote # Added import
warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy connectable")

# Load environment variables from .env file
load_dotenv()

# Database connection
PG_USER = os.getenv("WAREHOUSE_USER")
PG_PW = os.getenv("WAREHOUSE_PASSWORD")
PG_HOST = os.getenv("WAREHOUSE_HOST")
PG_PORT = os.getenv("WAREHOUSE_PORT")
PG_DB = os.getenv("WAREHOUSE_DB")

DATABASE_URL = f"postgresql+psycopg2://{PG_USER}:{PG_PW}@{PG_HOST}:{PG_PORT}/{PG_DB}"

@st.cache_resource
def get_engine():
    return create_engine(DATABASE_URL)

def fetch_data(query, params=None):
    engine = get_engine()
    actual_params = [] if params is None else params
    return pd.read_sql_query(query, engine, params=actual_params)

# =============================================================================
# DBT MODEL BASED FUNCTIONS - Simplified queries using pre-built DBT views
# =============================================================================

@st.cache_data
def get_artist_trends():
    """Fetch artist trends from DBT view - replaces complex CTE logic"""
    query = """
    SELECT * FROM analytics.artist_trends_dashboard
    LIMIT 50
    """
    return fetch_data(query)

@st.cache_data
def get_genre_trends():
    """Fetch genre trends from DBT view - replaces complex CTE logic"""
    query = """
    SELECT * FROM analytics.genre_trends_dashboard
    LIMIT 25
    """
    return fetch_data(query)

@st.cache_data
def get_platform_data():
    """Fetch platform comparison data from DBT view"""
    query = """
    SELECT * FROM analytics.platform_data_dashboard
    """
    return fetch_data(query)

@st.cache_data
def get_temporal_data():
    """Fetch temporal trends data from DBT view"""
    query = """
    SELECT * FROM analytics.temporal_data_dashboard
    """
    return fetch_data(query)

@st.cache_data
def get_wordcloud_data():
    """Fetch word cloud data from DBT view"""
    query = """
    SELECT * FROM analytics.wordcloud_data_dashboard
    """
    return fetch_data(query)

@st.cache_data
def get_overall_stats():
    """Get overall dashboard statistics from DBT view"""
    query = """
    SELECT * FROM analytics.overall_stats_dashboard
    """
    return fetch_data(query)

@st.cache_data
def get_trend_summary_data():
    """Fetch trend summary data from DBT view - simplified from multiple complex queries"""
    try:
        # Use the trend summary artists DBT view
        artists_query = """
        SELECT * FROM analytics.trend_summary_artists_dashboard
        ORDER BY trend_strength DESC, mentions DESC
        LIMIT 50
        """
        artists_data = fetch_data(artists_query)

        # Get overview data from flattened tables (keeping original as it's already optimized)
        overview_query = """
        SELECT * FROM analytics.trend_summary_overview
        ORDER BY analysis_timestamp DESC
        LIMIT 1
        """
        overview_data = fetch_data(overview_query)

        # Get top genres data with NaN filtering
        genres_query = """
        SELECT * FROM analytics.trend_summary_top_genres
        WHERE analysis_timestamp = (
            SELECT MAX(analysis_timestamp) FROM analytics.trend_summary_top_genres
        )
        AND LOWER(genre_name) != 'nan'
        AND LOWER(genre_name) != 'null'
        AND genre_name IS NOT NULL
        AND TRIM(genre_name) != ''
        ORDER BY popularity_score DESC
        LIMIT 15
        """
        genres_data = fetch_data(genres_query)

        # Get sentiment patterns
        sentiment_query = """
        SELECT * FROM analytics.trend_summary_sentiment_patterns
        ORDER BY analysis_timestamp DESC
        LIMIT 1
        """
        sentiment_data = fetch_data(sentiment_query)

        # Get engagement levels
        engagement_query = """
        SELECT * FROM analytics.trend_summary_engagement_levels
        ORDER BY analysis_timestamp DESC
        LIMIT 1
        """
        engagement_data = fetch_data(engagement_query)

        return {
            'overview': overview_data,
            'artists': artists_data,
            'genres': genres_data,
            'sentiment': sentiment_data,
            'engagement': engagement_data
        }
    except Exception as e:
        st.error(f"Error fetching trend summary data: {e}")
        return None

@st.cache_data
def get_insights_summary_data():
    """Fetch insights summary data from flattened tables (keeping original as already optimized)"""
    try:
        # Get overview data
        overview_query = """
        SELECT * FROM analytics.insights_summary_overview
        ORDER BY analysis_timestamp DESC
        LIMIT 1
        """
        overview_data = fetch_data(overview_query)

        # Get key findings
        findings_query = """
        SELECT * FROM analytics.insights_summary_key_findings
        WHERE analysis_timestamp = (
            SELECT MAX(analysis_timestamp) FROM analytics.insights_summary_key_findings
        )
        ORDER BY finding_order
        """
        findings_data = fetch_data(findings_query)

        # Get artist insights
        artist_insights_query = """
        SELECT * FROM analytics.insights_summary_artist_insights
        WHERE analysis_timestamp = (
            SELECT MAX(analysis_timestamp) FROM analytics.insights_summary_artist_insights
        )
        ORDER BY artist_name
        """
        artist_insights_data = fetch_data(artist_insights_query)

        return {
            'overview': overview_data,
            'findings': findings_data,
            'artist_insights': artist_insights_data
        }
    except Exception as e:
        st.error(f"Error fetching insights summary data: {e}")
        return None

@st.cache_data
def get_genre_artist_diversity():
    """Fetch genre artist diversity data from DBT view"""
    query = """
    SELECT * FROM analytics.genre_artist_diversity_dashboard
    """
    return fetch_data(query)

@st.cache_data
def get_artists_without_genre_count():
    """Count artists without genre assignment from DBT view"""
    query = """
    SELECT artists_without_genre FROM analytics.artists_without_genre_dashboard
    """
    result = fetch_data(query)
    return result['artists_without_genre'].iloc[0] if not result.empty else 0

@st.cache_data
def get_artist_sentiment_data():
    """Fetch artist sentiment data from DBT view - replaces complex CTE in dashboard"""
    query = """
    SELECT * FROM analytics.artist_sentiment_dashboard
    ORDER BY mention_count DESC
    LIMIT 50
    """
    return fetch_data(query)

# =============================================================================
# VISUALIZATION FUNCTIONS (unchanged from original)
# =============================================================================

def create_wordcloud_chart(df):
    """Create a word cloud from the database data"""
    if df.empty:
        st.warning("No word cloud data available")
        return None

    # Create word frequency dictionary
    word_freq = dict(zip(df['word'], df['frequency']))

    # Generate word cloud
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        colormap='viridis',
        max_words=100
    ).generate_from_frequencies(word_freq)

    # Create matplotlib figure
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title('🎵 Music Discussion Word Cloud', fontsize=16, fontweight='bold', pad=20)

    return fig

def create_artist_trends_chart(df):
    """Create an interactive artist trends visualization"""
    if df.empty:
        st.warning("No artist data available")
        return None

    fig = px.scatter(df,
                     x='mention_count',
                     y='sentiment_score',
                     size='trend_strength',
                     color='trend_direction',
                     hover_name='artist_name',
                     hover_data=['engagement_level'],
                     title="🎤 Artist Popularity vs Sentiment",
                     labels={'mention_count': 'Social Media Mentions', 'sentiment_score': 'Average Sentiment Score'},
                     color_discrete_map={'positive': '#28a745', 'negative': '#dc3545', 'neutral': '#6c757d'})

    fig.update_layout(
        height=500,
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_genre_radar_chart(df):
    """Create a radar chart for genre analysis"""
    if df.empty:
        st.warning("No genre data available")
        return None

    fig = go.Figure()

    for _, row in df.head(6).iterrows():  # Limit to top 6 genres for readability
        fig.add_trace(go.Scatterpolar(
            r=[row['mention_count']/df['mention_count'].max(),
               row['sentiment_score']/10,
               row['trend_strength'],
               row['popularity_score']],
            theta=['Mentions', 'Sentiment', 'Trend Strength', 'Popularity'],
            fill='toself',
            name=row['genre']
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        title="🎶 Genre Performance Radar",
        height=500
    )
    return fig

def create_platform_comparison(df):
    """Create platform comparison charts"""
    if df.empty:
        st.warning("No platform data available")
        return None

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Platform Activity', 'Average Sentiment by Platform'),
        specs=[[{"type": "bar"}, {"type": "bar"}]]
    )

    # Platform activity
    fig.add_trace(
        go.Bar(x=df['platform'], y=df['total_mentions'], name='Total Mentions', marker_color='#ff6b6b'),
        row=1, col=1
    )

    # Platform sentiment
    fig.add_trace(
        go.Bar(x=df['platform'], y=df['avg_sentiment'], name='Avg Sentiment', marker_color='#4ecdc4'),
        row=1, col=2
    )

    fig.update_layout(height=400, showlegend=False, title_text="📱 Platform Analysis")
    return fig

def create_temporal_trends(df):
    """Create temporal trends visualization showing sentiment shift only"""
    if df.empty:
        st.warning("No temporal data available")
        return None

    # Create a single plot for sentiment shift trends
    fig = go.Figure()

    # Sentiment shift trends with zero reference line
    fig.add_trace(
        go.Scatter(x=df['date'], y=df['sentiment_shift'],
                  mode='lines+markers', name='Sentiment Shift',
                  line=dict(color='#4ecdc4', width=3),
                  marker=dict(size=8))
    )

    # Add zero reference line for sentiment shift
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

    # Update layout
    fig.update_layout(
        height=400,
        showlegend=False,
        title_text="📈 Sentiment Shift Trends",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Date",
        yaxis_title="Sentiment Shift"
    )

    return fig

def create_genre_artist_diversity_chart(df):
    """Create a bar chart showing artist diversity by genre"""
    if df.empty:
        st.warning("No genre artist diversity data available")
        return None

    fig = px.bar(df,
                 x='genre',
                 y='artist_diversity',
                 color='popularity_score',
                 title="🎨 Artist Diversity by Genre",
                 labels={'artist_diversity': 'Number of Unique Artists', 'genre': 'Genre'},
                 color_continuous_scale='viridis')

    fig.update_layout(height=400)
    fig.update_xaxes(tickangle=45)

    return fig

# =============================================================================
# STREAMLIT UI (keeping the same structure but with DBT-powered data)
# =============================================================================

st.set_page_config(
    page_title="🎌 Japanese Music Trends Dashboard",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Japanese aesthetic
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

st.markdown('<div class="main-header"><h1>🎌 Japanese Music Trends Dashboard</h1><p>Social Media Analytics for J-Pop, City Pop, Anime Music & More</p><p><strong>🚀 Powered by DBT Models</strong></p></div>', unsafe_allow_html=True)

# Initialize session state for search functionality
if 'artist_search' not in st.session_state:
    st.session_state.artist_search = ""

st.sidebar.title("🎵 Navigation")
page = st.sidebar.radio("Choose a category", [
    "🏠 Overview",
    "🎤 Artist Trends",
    "🎶 Genre Analysis",
    "☁️ Word Cloud",
    "📱 Platform Insights",
    "💭 Sentiment Deep Dive",
    "📈 AI Trend Summary",
    "🔍 AI Insights"
])

# Load real data using DBT models
try:
    artist_data = get_artist_trends()
    if not artist_data.empty and 'artist_name' in artist_data.columns:
        artist_data['artist_name'] = artist_data['artist_name'].apply(lambda x: unquote(x) if isinstance(x, str) else x) # Added decoding

    genre_data = get_genre_trends()
    genre_artist_diversity_data = get_genre_artist_diversity()
    artists_without_genre_count = get_artists_without_genre_count()
    platform_data = get_platform_data()
    temporal_data = get_temporal_data()
    wordcloud_data = get_wordcloud_data()

    overall_stats_df = get_overall_stats()
    if overall_stats_df.empty:
        st.error("Error loading overall statistics: No data returned.")
        # Initialize with default/empty values or handle as appropriate
        stats = pd.Series({
            'total_extractions': 0, 'avg_sentiment': 0.0,
            'unique_artists': 0, 'positive_count': 0,
            'total_sentiment_count': 0
        })
    else:
        stats = overall_stats_df.iloc[0]
except Exception as e:
    import traceback
    st.error(f"Error loading data (see details below). Type: {type(e)}, Message: {str(e)}")
    st.text("Full Traceback:")
    st.text(traceback.format_exc())
    st.stop()

# New: Load trend summary and insights data
try:
    trend_summary_data = get_trend_summary_data()
    insights_summary_data = get_insights_summary_data()

    # Validate the data structure with better error handling
    if trend_summary_data is not None:
        if not isinstance(trend_summary_data, dict):
            st.warning(f"Trend summary data has unexpected format. Got {type(trend_summary_data)}, expected dict.")
            trend_summary_data = None
        else:
            for key, value in trend_summary_data.items():
                if not isinstance(value, pd.DataFrame):
                    st.warning(f"Trend summary data[{key}] has unexpected format. Got {type(value)}, expected DataFrame.")
                    # Replace with empty DataFrame to prevent errors
                    trend_summary_data[key] = pd.DataFrame()
                else:
                    if key == 'artists' and not value.empty and 'artist_name' in value.columns:
                        trend_summary_data[key]['artist_name'] = trend_summary_data[key]['artist_name'].apply(lambda x: unquote(x) if isinstance(x, str) else x)
                    elif key == 'genres' and not value.empty and 'genre_name' in value.columns:
                        trend_summary_data[key]['genre_name'] = trend_summary_data[key]['genre_name'].apply(lambda x: unquote(x) if isinstance(x, str) else x)

    if insights_summary_data is not None:
        if not isinstance(insights_summary_data, dict):
            st.warning(f"Insights summary data has unexpected format. Got {type(insights_summary_data)}, expected dict.")
            insights_summary_data = None
        else:
            for key, value in insights_summary_data.items():
                if not isinstance(value, pd.DataFrame):
                    st.warning(f"Insights summary data[{key}] has unexpected format. Got {type(value)}, expected DataFrame.")
                    # Replace with empty DataFrame to prevent errors
                    insights_summary_data[key] = pd.DataFrame()
                else:
                    if key == 'artist_insights' and not value.empty and 'artist_name' in value.columns:
                        insights_summary_data[key]['artist_name'] = value['artist_name'].apply(lambda x: unquote(x) if isinstance(x, str) else x)
                    elif key == 'overview' and not value.empty and 'executive_summary' in value.columns:
                        insights_summary_data[key]['executive_summary'] = value['executive_summary'].apply(lambda x: unquote(x) if isinstance(x, str) else x)

except Exception as e:
    st.error(f"Error loading summary data: {str(e)}")
    # Set default empty values to prevent crashes
    trend_summary_data = None
    insights_summary_data = None
    import traceback
    st.error(f"Traceback: {traceback.format_exc()}")
    st.stop()

if page == "🏠 Overview":
    st.header("🌟 Music Social Media Landscape")

    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_mentions = int(stats['total_extractions']) if not pd.isna(stats['total_extractions']) else 0
        st.metric("Total Extractions", f"{total_mentions:,}")

    with col2:
        avg_sentiment = float(stats['avg_sentiment']) if not pd.isna(stats['avg_sentiment']) else 5.0
        st.metric("Average Sentiment", f"{avg_sentiment:.1f}/10")

    with col3:
        unique_artists = int(stats['unique_artists']) if not pd.isna(stats['unique_artists']) else 0
        st.metric("Unique Artists", unique_artists)

    with col4:
        if stats['total_sentiment_count'] > 0:
            positive_pct = (stats['positive_count'] / stats['total_sentiment_count']) * 100
            st.metric("Positive Sentiment", f"{positive_pct:.1f}%")
        else:
            st.metric("Positive Sentiment", "N/A")

    st.markdown("---")

    # Main visualizations
    col1, col2 = st.columns([2, 1])

    with col1:
        if not artist_data.empty:
            fig = create_artist_trends_chart(artist_data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No artist data available")

    with col2:
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

    # Temporal overview with enhanced metrics
    if not temporal_data.empty:
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

        # Show engagement pattern distribution
        col1, col2 = st.columns([1, 1])


        with col1:
            # Sentiment trend interpretation
            st.subheader("📊 Sentiment Trend Status")
            if avg_sentiment_shift > 0.1:
                sentiment_status = "📈 Positive trend (sentiment improving)"
                status_color = "success"
            elif avg_sentiment_shift < -0.1:
                sentiment_status = "📉 Negative trend (sentiment declining)"
                status_color = "error"
            else:
                sentiment_status = "📊 Stable trend (sentiment steady)"
                status_color = "info"

            st.markdown(f"""
            <div class="metric-card">
                <h4>Current Trend</h4>
                <p style="color: {'green' if status_color == 'success' else 'red' if status_color == 'error' else 'blue'};">
                    {sentiment_status}
                </p>
                <p><small>Based on {time_periods} time periods analyzed</small></p>
            </div>
            """, unsafe_allow_html=True)

        # Show the enhanced temporal chart
        fig = create_temporal_trends(temporal_data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No temporal data available")

    # New: Trend summary overview
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
            total_artists = int(overview['total_artists_analyzed']) if pd.notna(overview['total_artists_analyzed']) else 0
            st.metric("Artists Analyzed", f"{total_artists:,}")
        with col3:
            total_genres = int(overview['total_genres_analyzed']) if pd.notna(overview['total_genres_analyzed']) else 0
            st.metric("Genres Analyzed", f"{total_genres:,}")
        with col4:
            time_periods = int(overview['time_periods_analyzed']) if pd.notna(overview['time_periods_analyzed']) else 0
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

elif page == "🎤 Artist Trends":
    st.header("🎤 Artist Deep Dive")

    if not artist_data.empty:
        # Artist selector
        selected_artist = st.selectbox("Select an artist for detailed analysis:", artist_data['artist_name'].tolist())
        artist_info = artist_data[artist_data['artist_name'] == selected_artist].iloc[0]

        # Artist overview
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Mentions", int(artist_info['mention_count']))
        with col2:
            st.metric("Sentiment Score", f"{artist_info['sentiment_score']:.1f}/10")
        with col3:
            st.metric("Trend Strength", f"{artist_info['trend_strength']:.2f}")

        # Artist comparison chart
        st.subheader("📊 Artist Comparison")
        fig = px.bar(artist_data.head(10),
                     x='artist_name',
                     y='mention_count',
                     color='sentiment_score',
                     title="Artist Mentions with Sentiment Coloring",
                     color_continuous_scale='RdYlGn')
        fig.update_layout(height=400)
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

        # Platform presence analysis
        st.subheader("📱 Platform Analysis")
        if not platform_data.empty:
            col1, col2 = st.columns(2)

            with col1:
                fig = px.pie(platform_data,
                           values='total_mentions',
                           names='platform',
                           title="Mentions Distribution by Platform")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                fig = px.bar(platform_data,
                           x='platform',
                           y='avg_sentiment',
                           title="Average Sentiment by Platform",
                           color='avg_sentiment',
                           color_continuous_scale='RdYlGn')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No platform data available")
    else:
        st.warning("No artist data available")

elif page == "🎶 Genre Analysis":
    st.header("🎶 Genre Landscape Analysis")

    if not genre_data.empty:
        col1, col2 = st.columns(2)

        with col1:
            fig = create_genre_radar_chart(genre_data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("📈 Genre Performance Metrics")

            # Genre rankings - limit to 5 genres to match radar chart height
            for i, (_, genre) in enumerate(genre_data.head(5).iterrows()):
                progress_value = float(genre['trend_strength'])
                st.write(f"**{genre['genre']}**")
                st.progress(min(progress_value, 1.0))  # Cap at 1.0 for progress bar
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.caption(f"Mentions: {int(genre['mention_count'])}")
                with col_b:
                    st.caption(f"Sentiment: {genre['sentiment_score']:.1f}")
                with col_c:
                    st.caption(f"Trend: {progress_value:.2f}")
                st.markdown("<br>", unsafe_allow_html=True)

        # Genre sentiment comparison - moved outside columns to fix layout
        st.subheader("🎵 Genre Sentiment Analysis")
        fig = px.bar(genre_data,
                     x='genre',
                     y='sentiment_score',
                     color='mention_count',
                     title="Sentiment Score by Genre",
                     color_continuous_scale='viridis')
        fig.update_layout(height=400)
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

        # Artist Diversity by Genre
        st.subheader("🎨 Artist Diversity by Genre")
        if not genre_artist_diversity_data.empty:
            fig = create_genre_artist_diversity_chart(genre_artist_diversity_data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

            # Show summary statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                max_diversity = genre_artist_diversity_data['artist_diversity'].max()
                if pd.notna(max_diversity):
                    st.metric("Highest Artist Diversity", f"{int(max_diversity)} artists")
                else:
                    st.metric("Highest Artist Diversity", "Unknown")
            with col2:
                avg_diversity = genre_artist_diversity_data['artist_diversity'].mean()
                if pd.notna(avg_diversity):
                    st.metric("Average Artist Diversity", f"{avg_diversity:.1f} artists")
                else:
                    st.metric("Average Artist Diversity", "Unknown")
            with col3:
                if artists_without_genre_count is not None:
                    st.metric("Artists Without Genre", f"{artists_without_genre_count} artists")
        else:
            st.info("No artist diversity data available")
    else:
        st.warning("No genre data available")

elif page == "☁️ Word Cloud":
    st.header("☁️ Music Discussion Word Cloud")

    if not wordcloud_data.empty:
        st.subheader("🎵 Most Discussed Terms")

        # Generate and display word cloud
        fig = create_wordcloud_chart(wordcloud_data)
        if fig:
            st.pyplot(fig)

        # Show top words table
        st.subheader("📊 Top Words by Frequency")
        top_words = wordcloud_data.head(20)

        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(top_words.head(10),
                        x='frequency',
                        y='word',
                        orientation='h',
                        title="Top 10 Words",
                        color='frequency',
                        color_continuous_scale='viridis')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.dataframe(top_words[['word', 'frequency']],
                        use_container_width=True,
                        height=400)
    else:
        st.warning("No word cloud data available")

elif page == "📱 Platform Insights":
    st.header("📱 Platform Performance Analysis")

    if not platform_data.empty:
        fig = create_platform_comparison(platform_data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

        # Platform details
        st.subheader("🔍 Platform Deep Dive")

        # Create tabs for each platform
        platform_names = platform_data['platform'].tolist()
        platform_tabs = st.tabs([f"📊 {platform}" for platform in platform_names])

        for i, (tab, platform_name) in enumerate(zip(platform_tabs, platform_names)):
            with tab:
                platform_info = platform_data[platform_data['platform'] == platform_name].iloc[0]

                st.markdown(f"### {platform_name} Analytics")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Mentions", int(platform_info['total_mentions']))
                    st.metric("Avg Sentiment", f"{platform_info['avg_sentiment']:.1f}/10")
                with col2:
                    if 'active_artists' in platform_info and not pd.isna(platform_info['active_artists']):
                        st.metric("Active Artists", int(platform_info['active_artists']))
                    else:
                        st.metric("Active Artists", "N/A")

                # Platform-specific metrics would go here
                st.info(f"Detailed {platform_name} analytics coming soon...")
    else:
        st.warning("No platform data available")

elif page == "💭 Sentiment Deep Dive":
    st.header("💭 Sentiment Analysis Deep Dive")

    try:
        # Get real sentiment data from DBT view
        sentiment_query = """
        SELECT
            overall_sentiment,
            sentiment_strength,
            COUNT(*) as count
        FROM analytics.sentiment_analysis
        WHERE overall_sentiment IS NOT NULL
        GROUP BY overall_sentiment, sentiment_strength
        ORDER BY overall_sentiment
        """
        sentiment_data_detailed = fetch_data(sentiment_query)

        # Get sentiment by artist using DBT view
        artist_sentiment_data = get_artist_sentiment_data()
        if not artist_sentiment_data.empty and 'artist_name' in artist_sentiment_data.columns:
            artist_sentiment_data['artist_name'] = artist_sentiment_data['artist_name'].apply(lambda x: unquote(x) if isinstance(x, str) else x) # Added decoding

        if not sentiment_data_detailed.empty:
            st.subheader("🎯 Overall Sentiment Landscape")

            # Sentiment distribution
            sentiment_dist = sentiment_data_detailed.groupby('overall_sentiment')['count'].sum()

            col1, col2 = st.columns(2)

            with col1:
                fig = px.pie(values=sentiment_dist.values,
                           names=sentiment_dist.index,
                           title="Overall Sentiment Distribution",
                           color_discrete_map={'positive': 'green', 'negative': 'red', 'neutral': 'gray'})
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("📊 Sentiment Insights")
                total_count = sentiment_dist.sum()
                positive_pct = (sentiment_dist.get('positive', 0) / total_count) * 100
                neutral_pct = (sentiment_dist.get('neutral', 0) / total_count) * 100
                negative_pct = (sentiment_dist.get('negative', 0) / total_count) * 100

                st.markdown(f"""
                <div class="metric-card">
                    <h4>Sentiment Breakdown</h4>
                    <p><span class="trend-positive">●</span> Positive: {positive_pct:.1f}%</p>
                    <p><span class="trend-neutral">●</span> Neutral: {neutral_pct:.1f}%</p>
                    <p><span class="trend-negative">●</span> Negative: {negative_pct:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)

                # Calculate overall health score
                avg_sentiment = sentiment_data_detailed['sentiment_strength'].mean()
                if avg_sentiment >= 7:
                    sentiment_status = "🔥 Excellent"
                elif avg_sentiment >= 5:
                    sentiment_status = "✅ Good"
                elif avg_sentiment >= 3:
                    sentiment_status = "⚠️ Moderate"
                else:
                    sentiment_status = "❌ Poor"

                st.markdown(f"""
                <div class="metric-card">
                    <h4>Overall Health</h4>
                    <p>Status: {sentiment_status}</p>
                    <p>Score: {avg_sentiment:.2f}/10</p>
                </div>
                """, unsafe_allow_html=True)

            # Artist sentiment analysis
            if not artist_sentiment_data.empty:
                st.subheader("🎤 Artist Sentiment Analysis")

                # Create sentiment heatmap (horizontal orientation)
                artist_pivot = artist_sentiment_data.pivot_table(
                    index='overall_sentiment',
                    columns='artist_name',
                    values='mention_count',
                    fill_value=0
                )

                # Limit to top 15 artists for better readability
                top_artists = artist_sentiment_data.groupby('artist_name')['mention_count'].sum().nlargest(15).index
                artist_pivot = artist_pivot[top_artists]

                if not artist_pivot.empty:
                    fig = px.imshow(artist_pivot.values,
                                  labels=dict(x="Artist", y="Sentiment", color="Mentions"),
                                  x=artist_pivot.columns,
                                  y=artist_pivot.index,
                                  color_continuous_scale='RdYlGn',
                                  title="Artist Sentiment Heatmap (Horizontal)")
                    fig.update_layout(height=300, width=None)  # Reduce height for horizontal layout
                    st.plotly_chart(fig, use_container_width=True)

                # Top artists by sentiment score
                top_artists = artist_sentiment_data.groupby('artist_name').agg({
                    'avg_sentiment_score': 'mean',
                    'mention_count': 'sum'
                }).reset_index()
                top_artists = top_artists.sort_values('avg_sentiment_score', ascending=False).head(10)

                if not top_artists.empty:
                    fig = px.bar(top_artists,
                               x='artist_name',
                               y='avg_sentiment_score',
                               title="Top Artists by Average Sentiment Score",
                               color='avg_sentiment_score',
                               color_continuous_scale='RdYlGn')
                    fig.update_layout(height=400)
                    fig.update_xaxes(tickangle=45)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No artist sentiment data available")

            # Sentiment vs Engagement correlation using real artist data
            if not artist_data.empty:
                st.subheader("🔗 Sentiment vs Engagement Correlation")
                engagement_mapping = {'high': 3, 'medium': 2, 'low': 1}
                correlation_data = artist_data.copy()
                correlation_data['engagement_numeric'] = correlation_data['engagement_level'].map(engagement_mapping)

                fig = px.scatter(correlation_data,
                               x='sentiment_score',
                               y='engagement_numeric',
                               size='mention_count',
                               hover_name='artist_name',
                               title="Sentiment Score vs Engagement Level",
                               labels={'sentiment_score': 'Sentiment Score', 'engagement_numeric': 'Engagement Level'})
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No sentiment data available")
    except Exception as e:
        st.error(f"Error loading sentiment data: {str(e)}")
        st.info("Please check the database connection and try again.")

elif page == "📈 AI Trend Summary":
    st.header("📈 AI-Generated Trend Summary")

    if trend_summary_data and not trend_summary_data['overview'].empty:
        # Overview Section
        overview = trend_summary_data['overview'].iloc[0]

        st.subheader("📊 Analysis Overview")
        col1, col2, col3 = st.columns(3)

        with col1:
            # Convert timestamp to string safely
            analysis_timestamp = pd.to_datetime(overview['analysis_timestamp'])
            if pd.notna(analysis_timestamp):
                analysis_date = analysis_timestamp.strftime("%Y-%m-%d")
            else:
                analysis_date = "N/A"
            st.metric("Analysis Date", analysis_date)
        with col2:
            total_artists = int(overview['total_artists_analyzed']) if pd.notna(overview['total_artists_analyzed']) else 0
            st.metric("Total Artists", f"{total_artists:,}")
        with col3:
            artists_count = len(trend_summary_data['artists']) if 'artists' in trend_summary_data and not trend_summary_data['artists'].empty else 0
            st.metric("Top Artists Count", artists_count)



        # Top Genres
        if not trend_summary_data['genres'].empty:
            st.subheader("🎶 Top Genres")
            genres_df = trend_summary_data['genres'].head(10)

            # Genre popularity chart
            fig = px.pie(genres_df,
                        values='popularity_score',
                        names='genre_name',
                        title="Genre Popularity Distribution")
            st.plotly_chart(fig, use_container_width=True)

        # Sentiment & Engagement Analytics
        col1, col2 = st.columns(2)

        with col1:
            if not trend_summary_data['sentiment'].empty:
                st.subheader("💭 Sentiment Patterns")
                sentiment = trend_summary_data['sentiment'].iloc[0]

                sentiment_data = pd.DataFrame({
                    'Sentiment': ['Positive', 'Negative', 'Neutral'],
                    'Trends': [sentiment['positive_trends'],
                              sentiment['negative_trends'],
                              sentiment['neutral_trends']]
                })

                fig = px.bar(sentiment_data, x='Sentiment', y='Trends',
                           color='Sentiment',
                           color_discrete_map={'Positive': 'green',
                                             'Negative': 'red',
                                             'Neutral': 'gray'})
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if not trend_summary_data['engagement'].empty:
                st.subheader("📊 Engagement Levels")
                engagement = trend_summary_data['engagement'].iloc[0]

                engagement_data = pd.DataFrame({
                    'Level': ['High', 'Medium', 'Low'],
                    'Count': [engagement['high_engagement'],
                             engagement['medium_engagement'],
                             engagement['low_engagement']]
                })

                fig = px.pie(engagement_data, values='Count', names='Level',
                           title="Engagement Distribution",
                           color_discrete_sequence=['#ff7f0e', '#2ca02c', '#d62728'])
                st.plotly_chart(fig, use_container_width=True)

        # Top Trending Artists
        st.subheader("🎤 Top Trending Artists")
        if not trend_summary_data['artists'].empty:
            artists_df = trend_summary_data['artists'].head(20)

            # Create an interactive chart
            fig = px.bar(artists_df,
                        x='trend_strength',
                        y='artist_name',
                        color='sentiment_score',
                        orientation='h',
                        title="Artist Trend Strength vs Sentiment",
                        color_continuous_scale='RdYlGn',
                        hover_data=['mentions', 'sentiment_direction'])
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)

            # Artists table with key metrics
            st.subheader("📋 Detailed Artist Metrics")
            display_artists = artists_df[['artist_name', 'trend_strength', 'mentions',
                                        'sentiment_score', 'sentiment_direction']].copy()
            display_artists.columns = ['Artist', 'Trend Strength', 'Mentions',
                                     'Sentiment Score', 'Sentiment Direction']
            st.dataframe(display_artists, use_container_width=True)
    else:
        st.warning("No trend summary data available")

elif page == "🔍 AI Insights":
    st.header("🔍 AI-Generated Music Insights")

    if insights_summary_data and 'overview' in insights_summary_data and not insights_summary_data['overview'].empty:
        # Executive Summary
        overview = insights_summary_data['overview'].iloc[0]

        st.subheader("📋 Executive Summary")
        col1, col2 = st.columns([2, 1])

        with col1:
            st.write(overview['executive_summary'])

        with col2:
            st.metric("Confidence Score", f"{overview['confidence_score']:.1%}")
            # Convert timestamp to string safely
            analysis_timestamp = pd.to_datetime(overview['analysis_timestamp'])
            if pd.notna(analysis_timestamp):
                analysis_date = analysis_timestamp.strftime("%Y-%m-%d")
            else:
                analysis_date = "N/A"
            st.metric("Analysis Date", analysis_date)

        # Key Findings
        if 'findings' in insights_summary_data and not insights_summary_data['findings'].empty:
            st.subheader("🔑 Key Findings")

            findings = insights_summary_data['findings']
            # Ensure 'finding_text' is decoded
            if 'finding_text' in findings.columns:
                findings['finding_text'] = findings['finding_text'].apply(lambda x: unquote(x) if isinstance(x, str) else x)

            for _, finding in findings.iterrows():
                st.write(f"**{finding['finding_order']}.** {finding['finding_text']}")

        # Artist-Specific Insights
        if 'artist_insights' in insights_summary_data and not insights_summary_data['artist_insights'].empty:
            st.subheader("🎤 Artist-Specific Insights")

            artist_insights = insights_summary_data['artist_insights']
            unique_artists = artist_insights['artist_name'].unique()

            # Search functionality
            col1, col2, col3 = st.columns([2, 1, 0.5])
            with col1:
                # Use session state for search term with default value
                default_search = st.session_state.get('artist_search', '')
                search_term = st.text_input("🔍 Search for artists or keywords in insights:",
                                          value=default_search,
                                          placeholder="e.g. 'Yoasobi', 'album', 'trending'...")
                # Update session state when search changes
                if search_term != st.session_state.get('artist_search', ''):
                    st.session_state.artist_search = search_term
            with col2:
                view_mode = st.selectbox("View Mode:", ["Search Results", "Browse All", "Summary Only"])
            with col3:
                st.write("")  # Empty space for alignment
                if st.button("🗑️ Clear", help="Clear search"):
                    st.session_state.artist_search = ""
                    st.rerun()

            # Filter insights based on search
            filtered_insights = artist_insights.copy()

            if search_term:
                # Search in both artist names and insight text (case insensitive)
                mask = (
                    artist_insights['artist_name'].str.contains(search_term, case=False, na=False) |
                    artist_insights['insight_text'].str.contains(search_term, case=False, na=False)
                )
                filtered_insights = artist_insights[mask]

                # Show search statistics
                if not filtered_insights.empty:
                    unique_artists_found = filtered_insights['artist_name'].nunique()
                    total_insights_found = len(filtered_insights)
                    st.info(f"🔍 Found **{total_insights_found}** insights for **{unique_artists_found}** artists matching '{search_term}'")
                else:
                    st.warning(f"🔍 No insights found for '{search_term}'. Try a different search term.")

            # Display current statistics
            current_artists = filtered_insights['artist_name'].nunique() if not filtered_insights.empty else 0
            current_insights = len(filtered_insights) if not filtered_insights.empty else 0

            if view_mode == "Summary Only":
                st.write(f"**Total Artists with Insights:** {len(unique_artists)}")
                if search_term:
                    st.write(f"**Filtered Results:** {current_insights} insights from {current_artists} artists")

                # Create a word cloud from filtered insights
                insights_text_list = filtered_insights['insight_text'].tolist()
                if insights_text_list:  # Check if list is not empty
                    all_insights_text = ' '.join(insights_text_list)

                    try:
                        from wordcloud import WordCloud
                        import matplotlib.pyplot as plt

                        if all_insights_text.strip():  # Check if text is not just whitespace
                            wordcloud = WordCloud(width=800, height=400,
                                                background_color='white',
                                                colormap='viridis').generate(all_insights_text)

                            fig, ax = plt.subplots(figsize=(10, 5))
                            ax.imshow(wordcloud, interpolation='bilinear')
                            ax.axis('off')
                            st.pyplot(fig)
                        else:
                            st.warning("No text available for word cloud generation")
                    except Exception as e:
                        st.error(f"Error generating word cloud: {e}")
                else:
                    st.warning("No insights text available for word cloud")

            elif view_mode == "Search Results" or view_mode == "Browse All":
                # Show appropriate message based on search state
                show_results = True
                if view_mode == "Search Results":
                    if not search_term:
                        st.info("💡 Enter a search term above to find specific artists or keywords in insights.")
                        show_results = False
                    elif filtered_insights.empty:
                        st.warning(f"🔍 No insights found for '{search_term}'. Try a different search term.")
                        show_results = False

                # Show filtered insights only if we should show results
                if show_results and not filtered_insights.empty:
                    # Limit results for better performance
                    if view_mode == "Browse All":
                        max_results = 20
                        if len(filtered_insights) > max_results:
                            st.info(f"📊 Showing first {max_results} of {current_insights} insights from {current_artists} artists. Use search to find specific content.")
                            display_insights = filtered_insights.head(max_results)
                        else:
                            display_insights = filtered_insights
                            st.info(f"📊 Showing all {current_insights} insights from {current_artists} artists.")
                    else:  # Search Results mode
                        display_insights = filtered_insights  # Show all search results

                    st.subheader("📝 Artist Insights")

                    # Group insights by artist for better organization
                    for artist_name in display_insights['artist_name'].unique():
                        artist_data_insights = display_insights[display_insights['artist_name'] == artist_name]

                        with st.expander(f"🎵 {artist_name} ({len(artist_data_insights)} insight{'s' if len(artist_data_insights) > 1 else ''})", expanded=len(display_insights['artist_name'].unique()) <= 3):
                            for _, insight in artist_data_insights.iterrows():
                                # Highlight search terms if searching
                                insight_text = insight['insight_text']
                                if search_term and view_mode == "Search Results":
                                    # Simple highlighting by making search term bold
                                    import re
                                    highlighted_text = re.sub(f'({re.escape(search_term)})',
                                                            r'**\1**',
                                                            insight_text,
                                                            flags=re.IGNORECASE)
                                    st.markdown(highlighted_text)
                                else:
                                    st.write(insight_text)
                else:
                    if view_mode == "Browse All":
                        st.warning("No insights available")

            # Quick artist selector for easy navigation
            if view_mode != "Summary Only":
                st.subheader("🎯 Quick Artist Selection")
                artist_cols = st.columns(min(5, len(unique_artists)))
                for i, artist in enumerate(sorted(unique_artists)[:15]):  # Show top 15 artists
                    with artist_cols[i % 5]:
                        if st.button(f"🎤 {artist}", key=f"artist_{i}", help=f"Search for {artist}"):
                            # Update search term to this artist and rerun
                            st.session_state.artist_search = artist
                            st.rerun()
    else:
        st.warning("No AI insights data available")

# Sidebar additional info
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Dashboard Stats")
current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M JST")
st.sidebar.metric("Last Updated", current_time)

try:
    total_data_points = int(stats['total_extractions']) if not pd.isna(stats['total_extractions']) else 0
    st.sidebar.metric("Data Points", f"{total_data_points:,}")
    active_artists = int(stats['unique_artists']) if not pd.isna(stats['unique_artists']) else 0
    st.sidebar.metric("Active Artists", active_artists)
except:
    st.sidebar.metric("Data Points", "Loading...")
    st.sidebar.metric("Active Artists", "Loading...")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Quick Insights")

try:
    if not artist_data.empty:
        top_artist = artist_data.iloc[0]
        st.sidebar.success(f"{top_artist['artist_name']} leads with {top_artist['mention_count']} mentions")
    else:
        st.sidebar.info("No artist data available")

    if not genre_data.empty:
        top_genre = genre_data.iloc[0]
        st.sidebar.info(f"{top_genre['genre']} dominates genre trends")
    else:
        st.sidebar.info("No genre data available")

    if not platform_data.empty:
        fastest_growing = platform_data.sort_values('total_mentions', ascending=False).iloc[0]
        st.sidebar.warning(f"Monitor {fastest_growing['platform']} growth")
    else:
        st.sidebar.warning("Monitor platform trends")
except Exception as e:
    st.sidebar.info("Loading insights...")
    st.sidebar.info("Real-time analytics")
    st.sidebar.info("Database connected")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🎌 Japanese Music Trends Dashboard | Powered by Social Media Analytics</p>
</div>
""", unsafe_allow_html=True)

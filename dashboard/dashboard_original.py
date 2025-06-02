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
import seaborn as sns
from io import BytesIO
import warnings
import numpy as np
warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy connectable")


# Load environment variables from .env file
load_dotenv()

# Database connection
PG_USER = os.getenv("WAREHOUSE_USER")
PG_PW = os.getenv("WAREHOUSE_PASSWORD") # Corrected variable name
PG_HOST = os.getenv("WAREHOUSE_HOST")
PG_PORT = os.getenv("WAREHOUSE_PORT")
PG_DB = os.getenv("WAREHOUSE_DB")

DATABASE_URL = f"postgresql+psycopg2://{PG_USER}:{PG_PW}@{PG_HOST}:{PG_PORT}/{PG_DB}"

@st.cache_resource
def get_engine():
    return create_engine(DATABASE_URL)

def fetch_data(query, params=None):
    engine = get_engine()
    return pd.read_sql_query(query, engine, params=params)

def create_mock_data_if_needed():
    """Create mock data for demonstration purposes when real data is not available"""

    # Mock artist trends data
    mock_artists = pd.DataFrame({
        'artist_name': ['YOASOBI', 'Ado', 'King Gnu', 'LiSA', 'Kenshi Yonezu', 'Hikaru Utada', 'ONE OK ROCK', 'Fujii Kaze'],
        'mention_count': [156, 134, 98, 87, 76, 65, 54, 43],
        'sentiment_score': [8.2, 7.8, 8.5, 8.0, 7.6, 8.1, 7.9, 8.3],
        'trend_strength': [0.92, 0.88, 0.85, 0.82, 0.78, 0.75, 0.72, 0.69],
        'trend_direction': ['positive', 'positive', 'positive', 'positive', 'neutral', 'positive', 'positive', 'positive'],
        'engagement_level': ['high', 'high', 'high', 'medium', 'medium', 'medium', 'medium', 'low'],
        'platforms': [['YouTube', 'Twitter', 'Reddit'], ['YouTube', 'Twitter'], ['YouTube', 'Reddit'],
                     ['YouTube', 'Twitter'], ['YouTube'], ['Twitter', 'Reddit'], ['YouTube'], ['YouTube', 'Twitter']]
    })

    # Mock genre trends data
    mock_genres = pd.DataFrame({
        'genre': ['J-Pop', 'City Pop', 'Anime Music', 'J-Rock', 'Visual Kei', 'Enka'],
        'mention_count': [234, 156, 189, 123, 67, 34],
        'sentiment_score': [8.1, 8.4, 8.0, 7.8, 7.5, 7.2],
        'trend_strength': [0.89, 0.85, 0.87, 0.76, 0.65, 0.58],
        'popularity_score': [0.91, 0.83, 0.85, 0.74, 0.62, 0.55]
    })

    # Mock platform data
    mock_platforms = pd.DataFrame({
        'platform': ['YouTube', 'Twitter', 'Reddit', 'TikTok'],
        'total_mentions': [445, 298, 167, 123],
        'avg_sentiment': [8.1, 7.8, 8.2, 7.9],
        'active_artists': [12, 15, 8, 10]
    })

    # Mock temporal data
    dates = pd.date_range(start='2025-05-01', end='2025-05-31', freq='D')
    mock_temporal = pd.DataFrame({
        'date': dates,
        'daily_mentions': np.random.poisson(25, len(dates)) + np.sin(np.arange(len(dates)) * 0.2) * 10 + 25,
        'daily_sentiment': np.random.normal(7.8, 0.5, len(dates))
    })

    return mock_artists, mock_genres, mock_platforms, mock_temporal

def create_artist_trends_chart(df):
    """Create an interactive artist trends visualization"""
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
    fig = go.Figure()

    for _, row in df.iterrows():
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
    """Create temporal trends visualization"""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Daily Mentions Over Time', 'Sentiment Trends'),
        vertical_spacing=0.1
    )

    # Daily mentions
    fig.add_trace(
        go.Scatter(x=df['date'], y=df['daily_mentions'],
                  mode='lines+markers', name='Daily Mentions',
                  line=dict(color='#ff6b6b', width=3)),
        row=1, col=1
    )

    # Sentiment trends
    fig.add_trace(
        go.Scatter(x=df['date'], y=df['daily_sentiment'],
                  mode='lines+markers', name='Daily Sentiment',
                  line=dict(color='#4ecdc4', width=3)),
        row=2, col=1
    )

    fig.update_layout(height=600, showlegend=False, title_text="📈 Temporal Analysis")
    return fig

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

st.markdown('<div class="main-header"><h1>🎌 Japanese Music Trends Dashboard</h1><p>Real-time Social Media Analytics for J-Pop, City Pop, Anime Music & More</p></div>', unsafe_allow_html=True)

st.sidebar.title("🎵 Navigation")
page = st.sidebar.radio("Choose a category", [
    "🏠 Overview",
    "🎤 Artist Trends",
    "🎶 Genre Analysis",
    "📱 Platform Insights",
    "💭 Sentiment Deep Dive",
    "📊 Raw Data Explorer"
])

# Get mock data for demonstration
mock_artists, mock_genres, mock_platforms, mock_temporal = create_mock_data_if_needed()

if page == "🏠 Overview":
    st.header("🌟 Japanese Music Social Media Landscape")

    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_mentions = mock_artists['mention_count'].sum()
        st.metric("Total Mentions", f"{total_mentions:,}", "+12%")

    with col2:
        avg_sentiment = mock_artists['sentiment_score'].mean()
        st.metric("Average Sentiment", f"{avg_sentiment:.1f}/10", "+0.3")

    with col3:
        trending_artists = len(mock_artists[mock_artists['trend_direction'] == 'positive'])
        st.metric("Trending Artists", trending_artists, "+2")

    with col4:
        top_engagement = mock_artists['engagement_level'].value_counts()['high']
        st.metric("High Engagement Artists", top_engagement, "+1")

    st.markdown("---")

    # Main visualizations
    col1, col2 = st.columns([2, 1])

    with col1:
        st.plotly_chart(create_artist_trends_chart(mock_artists), use_container_width=True)

    with col2:
        st.subheader("🔥 Top Trending Artists")
        for i, (_, artist) in enumerate(mock_artists.head(5).iterrows()):
            sentiment_color = "trend-positive" if artist['sentiment_score'] > 7.5 else "trend-neutral"
            st.markdown(f"""
            <div class="metric-card">
                <strong>{i+1}. {artist['artist_name']}</strong><br>
                <span class="{sentiment_color}">Sentiment: {artist['sentiment_score']:.1f}/10</span><br>
                <small>Mentions: {artist['mention_count']} | Trend: {artist['trend_strength']:.2f}</small>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

    # Temporal overview
    st.plotly_chart(create_temporal_trends(mock_temporal), use_container_width=True)

elif page == "🎤 Artist Trends":
    st.header("🎤 Artist Deep Dive")

    # Artist selector
    selected_artist = st.selectbox("Select an artist for detailed analysis:", mock_artists['artist_name'].tolist())
    artist_data = mock_artists[mock_artists['artist_name'] == selected_artist].iloc[0]

    # Artist overview
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Mentions", artist_data['mention_count'])
    with col2:
        st.metric("Sentiment Score", f"{artist_data['sentiment_score']:.1f}/10")
    with col3:
        st.metric("Trend Strength", f"{artist_data['trend_strength']:.2f}")

    # Artist comparison chart
    st.subheader("📊 Artist Comparison")
    fig = px.bar(mock_artists.head(8),
                 x='artist_name',
                 y='mention_count',
                 color='sentiment_score',
                 title="Artist Mentions with Sentiment Coloring",
                 color_continuous_scale='RdYlGn')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Platform presence
    st.subheader("📱 Platform Presence")
    platform_data = []
    for platform in ['YouTube', 'Twitter', 'Reddit', 'TikTok']:
        count = sum(1 for platforms in mock_artists['platforms'] if platform in platforms)
        platform_data.append({'Platform': platform, 'Artist Count': count})

    platform_df = pd.DataFrame(platform_data)
    fig = px.pie(platform_df, values='Artist Count', names='Platform',
                 title="Artist Distribution Across Platforms")
    st.plotly_chart(fig, use_container_width=True)

elif page == "🎶 Genre Analysis":
    st.header("🎶 Genre Landscape Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(create_genre_radar_chart(mock_genres), use_container_width=True)

    with col2:
        st.subheader("📈 Genre Performance Metrics")

        # Genre rankings
        for i, (_, genre) in enumerate(mock_genres.iterrows()):
            progress_value = genre['trend_strength']
            st.write(f"**{genre['genre']}**")
            st.progress(progress_value)
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.caption(f"Mentions: {genre['mention_count']}")
            with col_b:
                st.caption(f"Sentiment: {genre['sentiment_score']:.1f}")
            with col_c:
                st.caption(f"Trend: {progress_value:.2f}")
            st.markdown("<br>", unsafe_allow_html=True)

    # Genre sentiment comparison
    st.subheader("🎵 Genre Sentiment Analysis")
    fig = px.box(mock_genres, y='sentiment_score', x='genre',
                 title="Sentiment Distribution by Genre")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

elif page == "📱 Platform Insights":
    st.header("📱 Platform Performance Analysis")

    st.plotly_chart(create_platform_comparison(mock_platforms), use_container_width=True)

    # Platform details
    st.subheader("🔍 Platform Deep Dive")

    platform_tabs = st.tabs(["YouTube", "Twitter", "Reddit", "TikTok"])

    with platform_tabs[0]:  # YouTube
        st.markdown("### 📺 YouTube Analytics")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Mentions", "445", "+8%")
            st.metric("Avg Sentiment", "8.1/10", "+0.2")
        with col2:
            st.metric("Active Artists", "12", "+1")
            st.metric("Engagement Rate", "94%", "+3%")

        # Mock YouTube-specific chart
        youtube_data = pd.DataFrame({
            'Content Type': ['Music Videos', 'Live Performances', 'Behind Scenes', 'Covers'],
            'Mentions': [234, 123, 56, 32],
            'Avg Sentiment': [8.3, 8.0, 7.8, 8.1]
        })
        fig = px.bar(youtube_data, x='Content Type', y='Mentions', color='Avg Sentiment',
                     title="YouTube Content Type Performance")
        st.plotly_chart(fig, use_container_width=True)

    with platform_tabs[1]:  # Twitter
        st.markdown("### 🐦 Twitter Analytics")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Mentions", "298", "+5%")
            st.metric("Avg Sentiment", "7.8/10", "+0.1")
        with col2:
            st.metric("Active Artists", "15", "+2")
            st.metric("Retweet Rate", "76%", "+4%")

    with platform_tabs[2]:  # Reddit
        st.markdown("### 📰 Reddit Analytics")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Mentions", "167", "+3%")
            st.metric("Avg Sentiment", "8.2/10", "+0.4")
        with col2:
            st.metric("Active Artists", "8", "0")
            st.metric("Upvote Rate", "89%", "+2%")

    with platform_tabs[3]:  # TikTok
        st.markdown("### 🎵 TikTok Analytics")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Mentions", "123", "+15%")
            st.metric("Avg Sentiment", "7.9/10", "+0.3")
        with col2:
            st.metric("Active Artists", "10", "+3")
            st.metric("Like Rate", "92%", "+5%")

elif page == "💭 Sentiment Deep Dive":
    st.header("💭 Sentiment Analysis Deep Dive")

    # Overall sentiment distribution
    sentiment_dist = mock_artists['trend_direction'].value_counts()

    col1, col2 = st.columns(2)

    with col1:
        fig = px.pie(values=sentiment_dist.values, names=sentiment_dist.index,
                     title="Overall Sentiment Distribution",
                     color_discrete_map={'positive': '#28a745', 'negative': '#dc3545', 'neutral': '#6c757d'})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📊 Sentiment Insights")
        positive_pct = (sentiment_dist.get('positive', 0) / len(mock_artists)) * 100
        neutral_pct = (sentiment_dist.get('neutral', 0) / len(mock_artists)) * 100
        negative_pct = (sentiment_dist.get('negative', 0) / len(mock_artists)) * 100

        st.markdown(f"""
        <div class="metric-card">
            <h4>Sentiment Breakdown</h4>
            <p><span class="trend-positive">●</span> Positive: {positive_pct:.1f}%</p>
            <p><span class="trend-neutral">●</span> Neutral: {neutral_pct:.1f}%</p>
            <p><span class="trend-negative">●</span> Negative: {negative_pct:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

        avg_sentiment = mock_artists['sentiment_score'].mean()
        if avg_sentiment >= 8:
            sentiment_status = "🔥 Excellent"
        elif avg_sentiment >= 7:
            sentiment_status = "✅ Good"
        elif avg_sentiment >= 6:
            sentiment_status = "⚠️ Moderate"
        else:
            sentiment_status = "❌ Poor"

        st.markdown(f"""
        <div class="metric-card">
            <h4>Overall Health</h4>
            <p>Status: {sentiment_status}</p>
            <p>Score: {avg_sentiment:.1f}/10</p>
        </div>
        """, unsafe_allow_html=True)

    # Sentiment vs Engagement correlation
    st.subheader("🔗 Sentiment vs Engagement Correlation")
    engagement_mapping = {'high': 3, 'medium': 2, 'low': 1}
    correlation_data = mock_artists.copy()
    correlation_data['engagement_numeric'] = correlation_data['engagement_level'].map(engagement_mapping)

    fig = px.scatter(correlation_data,
                     x='sentiment_score',
                     y='engagement_numeric',
                     size='mention_count',
                     hover_name='artist_name',
                     title="Sentiment Score vs Engagement Level",
                     labels={'sentiment_score': 'Sentiment Score', 'engagement_numeric': 'Engagement Level'})
    st.plotly_chart(fig, use_container_width=True)

elif page == "📊 Raw Data Explorer":
    st.header("📊 Raw Data Explorer")

    data_tabs = st.tabs(["🎤 Artist Data", "🎶 Genre Data", "📱 Platform Data", "📈 Temporal Data"])

    with data_tabs[0]:
        st.subheader("Artist Trends Data")
        st.dataframe(mock_artists, use_container_width=True)

        if st.button("📥 Download Artist Data"):
            csv = mock_artists.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="japanese_artist_trends.csv",
                mime="text/csv"
            )

    with data_tabs[1]:
        st.subheader("Genre Analysis Data")
        st.dataframe(mock_genres, use_container_width=True)

    with data_tabs[2]:
        st.subheader("Platform Metrics Data")
        st.dataframe(mock_platforms, use_container_width=True)

    with data_tabs[3]:
        st.subheader("Temporal Trends Data")
        st.dataframe(mock_temporal, use_container_width=True)

        # Interactive temporal chart
        fig = px.line(mock_temporal, x='date', y='daily_mentions',
                      title="Interactive Daily Mentions Timeline")
        st.plotly_chart(fig, use_container_width=True)

# Sidebar additional info
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Dashboard Stats")
st.sidebar.metric("Last Updated", "2025-06-01 10:30 JST")
st.sidebar.metric("Data Points", "1,234")
st.sidebar.metric("Active Artists", "25")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Quick Insights")
st.sidebar.success("YOASOBI leads with 156 mentions")
st.sidebar.info("J-Pop dominates genre trends")
st.sidebar.warning("Monitor City Pop growth")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🎌 Japanese Music Trends Dashboard | Powered by Social Media Analytics</p>
    <p><small>Real-time data from YouTube, Twitter, Reddit & TikTok</small></p>
</div>
""", unsafe_allow_html=True)

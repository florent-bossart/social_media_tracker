#!/usr/bin/env python3
"""
Minimal Streamlit App for Database Testing
This is a self-contained app that doesn't rely on complex imports.
"""

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="🎌 Japanese Music Analytics",
    page_icon="🎵",
    layout="wide"
)

def get_database_connection():
    """Get database connection using Streamlit secrets."""
    if not hasattr(st, 'secrets') or 'database' not in st.secrets:
        st.error("❌ Database secrets not configured properly")
        st.stop()
    
    try:
        connection_string = f"postgresql+psycopg2://{st.secrets.database.username}:{st.secrets.database.password}@{st.secrets.database.host}:{st.secrets.database.port}/{st.secrets.database.database}?sslmode=require"
        engine = create_engine(connection_string)
        return engine
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        st.stop()

def load_data():
    """Load essential dashboard data."""
    engine = get_database_connection()
    
    data = {}
    
    try:
        with engine.connect() as conn:
            # Load overview data
            try:
                data['overview'] = pd.read_sql(
                    "SELECT * FROM analytics.trend_summary_overview",
                    conn
                )
            except:
                data['overview'] = pd.DataFrame()
            
            # Load top artists
            try:
                data['top_artists'] = pd.read_sql(
                    "SELECT * FROM analytics.trend_summary_top_artists LIMIT 20",
                    conn
                )
            except:
                data['top_artists'] = pd.DataFrame()
            
            # Load top genres
            try:
                data['top_genres'] = pd.read_sql(
                    "SELECT * FROM analytics.trend_summary_top_genres LIMIT 20",
                    conn
                )
            except:
                data['top_genres'] = pd.DataFrame()
            
            # Load temporal trends
            try:
                data['temporal'] = pd.read_sql(
                    "SELECT * FROM analytics.temporal_trends ORDER BY analysis_date",
                    conn
                )
            except:
                data['temporal'] = pd.DataFrame()
                
    except Exception as e:
        st.error(f"Error loading data: {e}")
        data = {
            'overview': pd.DataFrame(),
            'top_artists': pd.DataFrame(),
            'top_genres': pd.DataFrame(),
            'temporal': pd.DataFrame()
        }
    
    return data

def main():
    """Main dashboard function."""
    
    # Header
    st.title("🎌 Japanese Music Analytics Dashboard")
    st.markdown("**Real-time insights from social media trends**")
    
    # Load data
    with st.spinner("Loading dashboard data..."):
        data = load_data()
    
    # Check if we have any data
    has_data = any(not df.empty for df in data.values())
    
    if not has_data:
        st.warning("⚠️ No data found in the database. You may need to import your data first.")
        
        # Show connection test
        if st.button("Test Database Connection"):
            engine = get_database_connection()
            try:
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT version()"))
                    version = result.fetchone()[0]
                    st.success("✅ Database connection successful!")
                    st.info(f"PostgreSQL: {version[:50]}...")
                    
                    # Check schemas
                    schemas = pd.read_sql(
                        "SELECT schema_name FROM information_schema.schemata WHERE schema_name IN ('analytics', 'raw', 'intermediate')",
                        conn
                    )
                    if not schemas.empty:
                        st.success(f"✅ Found schemas: {', '.join(schemas['schema_name'])}")
                    else:
                        st.warning("⚠️ No analytics schemas found")
            except Exception as e:
                st.error(f"❌ Connection test failed: {e}")
        
        return
    
    # Overview metrics
    if not data['overview'].empty:
        st.subheader("📊 Analytics Overview")
        
        overview = data['overview'].iloc[0] if len(data['overview']) > 0 else {}
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Comments",
                f"{overview.get('total_comments', 0):,}"
            )
        
        with col2:
            st.metric(
                "Unique Artists",
                f"{overview.get('unique_artists', 0):,}"
            )
        
        with col3:
            st.metric(
                "Avg Sentiment",
                f"{overview.get('avg_sentiment_score', 0):.1f}"
            )
            
        with col4:
            st.metric(
                "Active Platforms",
                f"{overview.get('platforms_count', 0)}"
            )
    
    # Top Artists
    if not data['top_artists'].empty:
        st.subheader("🎤 Top Artists")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top artists chart
            fig = px.bar(
                data['top_artists'].head(10),
                x='mention_count',
                y='artist_name',
                orientation='h',
                title="Most Mentioned Artists",
                color='sentiment_score',
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Artists table
            st.dataframe(
                data['top_artists'][['artist_name', 'mention_count', 'sentiment_score']].head(10),
                use_container_width=True
            )
    
    # Top Genres
    if not data['top_genres'].empty:
        st.subheader("🎵 Top Genres")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Genre pie chart
            fig = px.pie(
                data['top_genres'].head(8),
                values='mention_count',
                names='genre_name',
                title="Genre Distribution"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Genres table
            st.dataframe(
                data['top_genres'][['genre_name', 'mention_count', 'avg_sentiment']].head(10),
                use_container_width=True
            )
    
    # Temporal Trends
    if not data['temporal'].empty:
        st.subheader("📈 Temporal Trends")
        
        # Convert date column
        if 'analysis_date' in data['temporal'].columns:
            data['temporal']['analysis_date'] = pd.to_datetime(data['temporal']['analysis_date'])
            
            fig = px.line(
                data['temporal'],
                x='analysis_date',
                y='mention_count',
                title="Activity Over Time",
                color='platform' if 'platform' in data['temporal'].columns else None
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("🚀 **Powered by Streamlit and Supabase** | Built with ❤️ for Japanese Music Analytics")

if __name__ == "__main__":
    main()

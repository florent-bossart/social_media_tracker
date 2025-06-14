"""
Artist Analytics Hub - Consolidated artist analysis page.
Combines Artist Trends, Sentiment Analysis, Content Discovery, and Author Influence.
"""

import streamlit as st
import pandas as pd
from ui_library import (
    StandardComponents, StandardCharts, PageLayouts, UITheme
)
from data_manager import DataManager

def artist_analytics_hub_page():
    """Unified artist analytics page with multiple analysis views"""
    
    # Page header
    StandardComponents.page_header(
        title="Artist Analytics Hub",
        icon="🎤",
        description="""
        **Comprehensive Artist Intelligence Center** - Your one-stop destination for deep artist insights.
        
        **What you'll find here:**
        - **🔥 Trending Artists**: Real-time popularity and mention tracking
        - **💭 Sentiment Analysis**: Public perception and emotional response analysis  
        - **🔗 Content Discovery**: Source tracking and content context analysis
        - **👥 Author Influence**: Key opinion leaders and community influencers
        - **📊 Cross-Platform Metrics**: Unified view across Reddit and YouTube
        
        **How to use:**
        - Use the tabs below to switch between different analysis views
        - Select specific artists to compare and analyze
        - Export data and insights for further analysis
        """
    )

    # Load all artist-related data
    with st.spinner("Loading artist analytics data..."):
        artist_data = DataManager.get_artist_analytics_hub_data()

    # Create tabbed interface for different analysis views
    tab_config = {
        "🔥 Trending Artists": lambda: trending_artists_tab(artist_data['trends']),
        "💭 Sentiment Analysis": lambda: sentiment_analysis_tab(artist_data['sentiment']),
        "🔗 Content Discovery": lambda: content_discovery_tab(artist_data['enriched'], artist_data['url_analysis']),
        "👥 Author Influence": lambda: author_influence_tab(artist_data['author_influence']),
        "📊 Artist Comparison": lambda: artist_comparison_tab(artist_data)
    }
    
    PageLayouts.tabbed_content(tab_config)

def trending_artists_tab(trends_df: pd.DataFrame):
    """Trending artists analysis tab"""
    st.subheader("🔥 Artist Trend Analysis")
    
    if trends_df.empty:
        StandardComponents.empty_state(
            "No Trending Data Available",
            "Artist trending data is currently unavailable. Please check back later.",
            "📈"
        )
        return

    # Key metrics
    if not trends_df.empty:
        total_artists = len(trends_df)
        avg_sentiment = trends_df['sentiment_score'].mean() if 'sentiment_score' in trends_df.columns else 0
        top_mentions = trends_df['mention_count'].max() if 'mention_count' in trends_df.columns else 0
        
        metrics = {
            "Total Artists": f"{total_artists:,}",
            "Avg Sentiment": f"{avg_sentiment:.1f}/10",
            "Top Mentions": f"{top_mentions:,}",
            "Active Platforms": "Reddit + YouTube"
        }
        StandardComponents.metric_cards(metrics)

    # Artist selection for detailed analysis
    st.subheader("📊 Top 20 Trending Artists by Mentions")
    
    # Main trending chart - full width for better visibility
    if 'artist_name' in trends_df.columns and 'mention_count' in trends_df.columns:
        fig = StandardCharts.create_bar_chart(
            trends_df.head(20),
            x_col='artist_name',
            y_col='mention_count',
            title="Top 20 Trending Artists by Mentions",
            horizontal=True
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    # Detailed data table
    st.subheader("📋 Detailed Artist Data")
    display_columns = ['artist_name', 'mention_count', 'sentiment_score', 'trend_strength', 'avg_comment_length']
    available_columns = [col for col in display_columns if col in trends_df.columns]
    
    StandardComponents.data_table(
        trends_df,
        title="Artist Trends Data",
        searchable=True,
        columns=available_columns,
        max_rows=20
    )

def sentiment_analysis_tab(sentiment_df: pd.DataFrame):
    """Sentiment analysis tab"""
    st.subheader("💭 Artist Sentiment Analysis")
    
    if sentiment_df.empty:
        StandardComponents.empty_state(
            "No Sentiment Data Available",
            "Sentiment analysis data is currently unavailable. Please check back later.",
            "💭"
        )
        return

    # Sentiment overview metrics
    if not sentiment_df.empty and 'sentiment_score' in sentiment_df.columns:
        avg_sentiment = sentiment_df['sentiment_score'].mean()
        positive_count = len(sentiment_df[sentiment_df['sentiment_score'] > 6.5])
        negative_count = len(sentiment_df[sentiment_df['sentiment_score'] < 4.5])
        
        metrics = {
            "Average Sentiment": f"{avg_sentiment:.1f}/10",
            "Positive Artists": f"{positive_count}",
            "Negative Artists": f"{negative_count}",
            "Neutral Artists": f"{len(sentiment_df) - positive_count - negative_count}"
        }
        StandardComponents.metric_cards(metrics)

    # Sentiment distribution chart
    col1, col2 = st.columns(2)
    
    with col1:
        if 'sentiment_score' in sentiment_df.columns:
            # Sentiment histogram
            import plotly.express as px
            fig = px.histogram(
                sentiment_df,
                x='sentiment_score',
                nbins=20,
                title="Sentiment Score Distribution",
                labels={'sentiment_score': 'Sentiment Score (1-10)', 'count': 'Number of Artists'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top positive/negative artists
        if 'sentiment_score' in sentiment_df.columns and 'artist_name' in sentiment_df.columns:
            top_positive = sentiment_df.nlargest(5, 'sentiment_score')
            st.subheader("😊 Most Positive")
            for _, artist in top_positive.iterrows():
                st.write(f"• {artist['artist_name']}: {artist['sentiment_score']:.1f}")
                
            st.subheader("😔 Most Negative") 
            bottom_negative = sentiment_df.nsmallest(5, 'sentiment_score')
            for _, artist in bottom_negative.iterrows():
                st.write(f"• {artist['artist_name']}: {artist['sentiment_score']:.1f}")

    # Sentiment vs Mentions scatter plot
    if all(col in sentiment_df.columns for col in ['sentiment_score', 'mention_count', 'artist_name']):
        fig = StandardCharts.create_scatter_plot(
            sentiment_df.head(50),
            x_col='mention_count',
            y_col='sentiment_score',
            title="Sentiment vs Popularity",
            hover_data=['artist_name']
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True)

def content_discovery_tab(enriched_df: pd.DataFrame, url_df: pd.DataFrame):
    """Content discovery and source analysis tab"""
    st.subheader("🔗 Content Discovery & Source Analysis")
    
    if enriched_df.empty and url_df.empty:
        StandardComponents.empty_state(
            "No Content Data Available",
            "Content discovery data is currently being processed. Please check back later.",
            "🔗"
        )
        return

    # Content metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Enriched Artist Data")
        if not enriched_df.empty:
            # Show key metrics from enriched data
            total_contexts = len(enriched_df)
            unique_artists = enriched_df['artist_name'].nunique() if 'artist_name' in enriched_df.columns else 0
            
            st.metric("Total Contexts", f"{total_contexts:,}")
            st.metric("Unique Artists", unique_artists)
            
            # Top artists by mentions
            if 'artist_name' in enriched_df.columns and 'total_mentions' in enriched_df.columns:
                top_enriched = enriched_df.groupby('artist_name')['total_mentions'].sum().sort_values(ascending=False).head(10)
                fig = StandardCharts.create_bar_chart(
                    top_enriched.reset_index(),
                    x_col='artist_name',
                    y_col='total_mentions',
                    title="Top Artists by Total Mentions",
                    horizontal=True
                )
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Enriched artist data not available yet")
    
    with col2:
        st.subheader("🌐 URL Analysis")
        if not url_df.empty:
            # URL analysis metrics
            total_urls = len(url_df)
            avg_mentions = url_df['mention_count'].mean() if 'mention_count' in url_df.columns else 0
            
            st.metric("Total URLs", f"{total_urls:,}")
            st.metric("Avg Mentions per URL", f"{avg_mentions:.1f}")
            
            # Top URLs by mentions
            if 'url' in url_df.columns and 'mention_count' in url_df.columns:
                StandardComponents.data_table(
                    url_df.head(10),
                    title="Top URLs by Mentions",
                    columns=['url', 'mention_count', 'artist_name'],
                    max_rows=10
                )
        else:
            st.info("URL analysis data not available yet")

    # Combined content table
    if not enriched_df.empty:
        st.subheader("📋 Detailed Content Data")
        display_columns = ['artist_name', 'source_platform', 'total_mentions', 'video_title', 'channel_title_clean']
        available_columns = [col for col in display_columns if col in enriched_df.columns]
        
        StandardComponents.data_table(
            enriched_df,
            title="Enriched Content Context",
            searchable=True,
            columns=available_columns,
            max_rows=20
        )

def author_influence_tab(influence_df: pd.DataFrame):
    """Author influence analysis tab"""
    st.subheader("👥 Author Influence Analysis")
    
    if influence_df.empty:
        StandardComponents.empty_state(
            "No Influence Data Available",
            "Author influence data is currently being processed. Please check back later.",
            "👥"
        )
        return

    # Influence metrics
    if not influence_df.empty:
        total_authors = len(influence_df)
        avg_mentions = influence_df['total_mentions'].mean() if 'total_mentions' in influence_df.columns else 0
        top_influence = influence_df['total_mentions'].max() if 'total_mentions' in influence_df.columns else 0
        
        metrics = {
            "Total Authors": f"{total_authors:,}",
            "Avg Mentions": f"{avg_mentions:.1f}",
            "Top Influencer": f"{top_influence:,} mentions",
            "Analysis Type": "Cross-Platform"
        }
        StandardComponents.metric_cards(metrics)

    # Top influencers chart
    if 'author_name' in influence_df.columns and 'total_mentions' in influence_df.columns:
        fig = StandardCharts.create_bar_chart(
            influence_df.head(15),
            x_col='author_name',
            y_col='total_mentions',
            title="Top 15 Most Influential Authors",
            horizontal=True
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    # Detailed influence table
    display_columns = ['author_name', 'total_mentions', 'unique_artists', 'platforms', 'avg_sentiment']
    available_columns = [col for col in display_columns if col in influence_df.columns]
    
    StandardComponents.data_table(
        influence_df,
        title="Author Influence Rankings",
        searchable=True,
        columns=available_columns,
        max_rows=25
    )

def artist_comparison_tab(all_data: dict):
    """Artist comparison and cross-analysis tab"""
    st.subheader("📊 Artist Comparison Tool")
    
    # Get available artists from trends data
    trends_df = all_data.get('trends', pd.DataFrame())
    
    if trends_df.empty or 'artist_name' not in trends_df.columns:
        StandardComponents.empty_state(
            "No Artists Available for Comparison",
            "Artist data is currently unavailable. Please check back later.",
            "📊"
        )
        return

    # Artist selection
    selected_artists = StandardComponents.data_selector(
        trends_df,
        column='artist_name',
        label="Select artists to compare (up to 10):",
        multi=True,
        default_count=5
    )

    if not selected_artists:
        st.info("Please select artists to compare")
        return

    # Filter data for selected artists
    comparison_data = trends_df[trends_df['artist_name'].isin(selected_artists)]
    
    if comparison_data.empty:
        st.warning("No data found for selected artists")
        return

    # Comparison charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Mentions comparison
        if 'mention_count' in comparison_data.columns:
            fig = StandardCharts.create_bar_chart(
                comparison_data,
                x_col='artist_name',
                y_col='mention_count',
                title="Mentions Comparison",
                horizontal=False
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Sentiment comparison
        if 'sentiment_score' in comparison_data.columns:
            fig = StandardCharts.create_bar_chart(
                comparison_data,
                x_col='artist_name', 
                y_col='sentiment_score',
                title="Sentiment Comparison",
                horizontal=False
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)

    # Comparison table
    display_columns = ['artist_name', 'mention_count', 'sentiment_score', 'trend_strength', 'platform_count']
    available_columns = [col for col in display_columns if col in comparison_data.columns]
    
    StandardComponents.data_table(
        comparison_data,
        title="Selected Artists Comparison",
        columns=available_columns
    )

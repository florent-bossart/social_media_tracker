"""
Dashboard Pages module for the Japanese Music Trends Dashboard.
Contains the logic for each individual page/section of the dashboard.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from data_manager import DataManager
from visualizations import (
    create_artist_trends_chart, create_genre_radar_chart,
    create_genre_artist_diversity_chart, create_wordcloud_chart,
    create_platform_comparison, create_temporal_trends,
    create_artist_bar_chart, create_sentiment_distribution_chart
)
from ui_components import (
    display_metrics_row, display_top_artists_sidebar,
    display_temporal_summary,
    display_artist_details
)

def overview_page(stats, artist_data, temporal_data):
    """Render the overview page"""
    st.header("🌟 Music Social Media Landscape")

    # Add explanation of what this page shows
    with st.expander("ℹ️ What does this analysis show?", expanded=False):
        st.markdown("""
        This overview provides a **high-level snapshot** of Japanese music trends across social media platforms.
        
        **Key Insights:**
        - **Top Artists**: Most mentioned Japanese music artists across Reddit and YouTube
        - **Social Media Activity**: Overall engagement and discussion volume
        - **Trending Patterns**: How music discussions evolve over time
        - **Platform Reach**: Cross-platform presence and influence
        
        **What this tells us:**
        - Which artists are currently generating the most buzz
        - Overall health and activity of the Japanese music community online
        - Emerging trends and discussion patterns
        - Real-time social media engagement across platforms
        """)

    # Key metrics row
    display_metrics_row(stats)
    st.markdown("---")

    # Main visualizations
    if not artist_data.empty:
        st.subheader("🎤 Top Artist Trends")
        fig = create_artist_trends_chart(artist_data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No artist data available")

    # Temporal overview
    display_temporal_summary(temporal_data)

    # Show the temporal chart
    if not temporal_data.empty:
        fig = create_temporal_trends(temporal_data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

def artist_trends_page(artist_data, platform_data):
    """Render the artist trends page"""
    st.header("🎤 Artist Deep Dive")

    # Add explanation of what this page shows
    with st.expander("ℹ️ What does this analysis show?", expanded=False):
        st.markdown("""
        This page provides **detailed analysis** of individual Japanese music artists and their social media presence.
        
        **Key Features:**
        - **Multi-Artist Selection**: Compare up to 20 artists simultaneously
        - **Cross-Platform Metrics**: See how artists perform on Reddit vs YouTube
        - **Sentiment Analysis**: Understand public perception of each artist
        - **Engagement Tracking**: Monitor mentions, discussions, and community activity
        
        **How to use:**
        - Select multiple artists from the dropdown to compare their metrics
        - View the top 20 artists chart to see overall popularity rankings
        - Check platform analysis to understand where each artist has the strongest presence
        """)

    if not artist_data.empty:
        # Multiple artist selector for detailed analysis
        st.subheader("🔍 Artist Selection")
        
        # Multi-select for comparing multiple artists
        selected_artists = st.multiselect(
            "Select artists for detailed analysis:",
            options=artist_data['artist_name'].tolist(),
            default=artist_data['artist_name'].tolist()[:3],  # Default to top 3 artists
            help="You can select multiple artists to compare their metrics"
        )

        # Display detailed analysis for selected artists
        if selected_artists:
            st.subheader("📊 Selected Artists Overview")
            
            # Create columns for metrics display
            cols = st.columns(min(len(selected_artists), 4))  # Max 4 columns
            for i, artist_name in enumerate(selected_artists[:4]):  # Show first 4 artists in metrics
                artist_info = artist_data[artist_data['artist_name'] == artist_name].iloc[0]
                with cols[i % 4]:
                    st.metric(
                        label=f"🎤 {artist_name}",
                        value=f"{int(artist_info['mention_count'])} mentions",
                        delta=f"Sentiment: {artist_info['sentiment_score']:.1f}/10"
                    )
            
            # Show additional metrics if more than 4 artists selected
            if len(selected_artists) > 4:
                st.info(f"Showing metrics for first 4 artists. Total selected: {len(selected_artists)}")

        # Artist comparison chart (always show top 20)
        st.subheader("📊 Artist Comparison (Top 20)")
        fig = create_artist_bar_chart(artist_data, "Artist Mentions with Sentiment Coloring", num_artists=20)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

        # Detailed analysis for first selected artist (if any)
        if selected_artists:
            primary_artist = selected_artists[0]
            artist_info = artist_data[artist_data['artist_name'] == primary_artist].iloc[0]
            
            st.subheader(f"🎯 Detailed Analysis: {primary_artist}")
            display_artist_details(artist_info)

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

def genre_analysis_page(genre_data, genre_artist_diversity_data, artists_without_genre_count):
    """Render the genre analysis page"""
    st.header("🎶 Genre Landscape Analysis")

    # Add explanation of what this page shows
    with st.expander("ℹ️ What does this analysis show?", expanded=False):
        st.markdown("""
        This page analyzes **Japanese music genres** and their popularity patterns across social media.
        
        **Key Insights:**
        - **Genre Performance**: Which genres are trending and generating discussion
        - **Sentiment by Genre**: How different genres are perceived by audiences
        - **Artist Diversity**: Which genres have the most varied artist representation
        - **Trend Strength**: Measurement of genre momentum and growth
        
        **What this tells us:**
        - Which genres are currently popular in Japanese music discussions
        - How genre preferences vary across platforms
        - Emerging genre trends and shifts in musical taste
        """)

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

        # Genre sentiment comparison
        st.subheader("🎵 Genre Sentiment Analysis")
        fig = px.bar(genre_data,
                     x='genre',
                     y='sentiment_score',
                     color='sentiment_score',
                     title="Sentiment Score by Genre",
                     color_continuous_scale='RdYlGn')
        fig.update_layout(height=400)
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

        # Artist Diversity by Genre
        st.subheader("🎨 Artist Diversity by Genre")
        if not genre_artist_diversity_data.empty:
            # Filter to top 20 genres with the most artists for better visualization
            top_20_diversity_data = genre_artist_diversity_data.nlargest(20, 'artist_diversity')


            fig = create_genre_artist_diversity_chart(top_20_diversity_data)
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

def wordcloud_page(wordcloud_data):
    """Render the word cloud page"""
    st.header("☁️ Music Discussion Word Cloud")

    # Add explanation of what this page shows
    with st.expander("ℹ️ What does this analysis show?", expanded=False):
        st.markdown("""
        This page visualizes the **most frequently used words** in Japanese music discussions across social media.
        
        **Key Features:**
        - **Word Cloud Visualization**: Visual representation where larger words appear more frequently
        - **Frequency Analysis**: Detailed breakdown of word usage statistics
        - **Content Insights**: Understanding what topics and terms dominate music conversations
        
        **What this tells us:**
        - Common themes and topics in Japanese music discussions
        - Popular terminology and slang used by the community
        - Trending topics and recurring conversation patterns
        """)

    if not wordcloud_data.empty:
        st.subheader("🎵 Most Discussed Terms")

        # Generate and display word cloud
        fig = create_wordcloud_chart(wordcloud_data)
        if fig:
            st.pyplot(fig)

        # Show top words table
        st.subheader("📊 Top Words by Frequency")
        top_words = wordcloud_data.head(20).copy()
        top_words.index = range(1, len(top_words) + 1)
        st.dataframe(top_words, use_container_width=True)

        # Word frequency distribution
        fig = px.bar(wordcloud_data.head(15),
                     x='word',
                     y='frequency',
                     title="Top 15 Words by Frequency",
                     color='frequency',
                     color_continuous_scale='viridis')
        fig.update_layout(height=400)
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No word cloud data available")

def platform_insights_page(platform_data, video_context_data=None):
    """Render the enhanced platform insights page with video context"""
    st.header("📱 Platform Insights & Video Context")

    # Add explanation of what this page shows
    with st.expander("ℹ️ What does this analysis show?", expanded=False):
        st.markdown("""
        This page compares **Japanese music discussions** across different social media platforms with enhanced video context.
        
        **Key Features:**
        - **Cross-Platform Analysis**: Compare activity between Reddit and YouTube
        - **Video Context**: Understanding which video content drives discussions
        - **Content Performance**: Which videos and channels generate the most engagement
        - **Platform Sentiment**: How positive/negative discussions are per platform
        
        **What this tells us:**
        - Where Japanese music fans are most active online
        - Which video content resonates most with audiences
        - Platform-specific engagement patterns and community behavior
        """)

    # Create tabs for different analysis views
    tab1, tab2 = st.tabs(["📊 Platform Comparison", "🎬 Video Context Analysis"])
    
    with tab1:
        platform_comparison_section(platform_data)
    
    with tab2:
        video_context_section(video_context_data)

def platform_comparison_section(platform_data):
    """Platform comparison analysis section"""
    if not platform_data.empty:
        # Overview metrics
        total_mentions = platform_data['total_mentions'].sum()
        avg_sentiment_all = platform_data['avg_sentiment'].mean()
        most_active_platform = platform_data.loc[platform_data['total_mentions'].idxmax(), 'platform']

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Mentions (All Platforms)", f"{total_mentions:,}")
        with col2:
            st.metric("Average Sentiment", f"{avg_sentiment_all:.2f}/10")
        with col3:
            st.metric("Most Active Platform", most_active_platform)

        st.markdown("---")

        # Platform comparison chart
        fig = create_platform_comparison(platform_data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

        # Platform details table
        st.subheader("📊 Platform Details")
        platform_display = platform_data.copy()
        platform_display['avg_sentiment'] = platform_display['avg_sentiment'].round(2)
        st.dataframe(platform_display, use_container_width=True)
    else:
        st.warning("No platform data available")

def video_context_section(video_context_data):
    """Video context analysis section"""
    st.subheader("🎬 Video Content Analysis")
    
    if video_context_data is None or video_context_data.empty:
        st.info("Video context data is being processed. Check back later for detailed video insights.")
        return
    
    # Video context metrics
    total_videos = len(video_context_data)
    total_video_mentions = video_context_data['total_artist_mentions'].sum() if 'total_artist_mentions' in video_context_data.columns else 0
    unique_channels = video_context_data['channel_title_clean'].nunique() if 'channel_title_clean' in video_context_data.columns else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Videos Analyzed", f"{total_videos:,}")
    with col2:
        st.metric("Video-Related Mentions", f"{total_video_mentions:,}")
    with col3:
        st.metric("Unique Channels", f"{unique_channels:,}")
    
    # Top videos by mentions
    if 'total_artist_mentions' in video_context_data.columns and 'video_title' in video_context_data.columns:
        st.subheader("🔥 Most Discussed Videos")
        top_videos = video_context_data.nlargest(10, 'total_artist_mentions')
        
        for i, (_, video) in enumerate(top_videos.iterrows(), 1):
            with st.expander(f"{i}. {video['video_title'][:60]}... ({video['total_artist_mentions']} mentions)", expanded=i <= 3):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**Channel:** {video.get('channel_title_clean', 'Unknown')}")
                    st.write(f"**Artists Mentioned:** {video.get('artist_name', 'Unknown')}")
                    if 'sentiment_score' in video:
                        st.write(f"**Sentiment:** {video['sentiment_score']:.1f}/10")
                with col2:
                    st.metric("Mentions", f"{video['total_artist_mentions']}")
                    if 'engagement_score' in video:
                        st.metric("Engagement", f"{video['engagement_score']:.2f}")
    
    # Top channels by activity
    if 'channel_title_clean' in video_context_data.columns:
        st.subheader("📺 Most Active Channels")
        channel_activity = video_context_data.groupby('channel_title_clean')['total_artist_mentions'].sum().sort_values(ascending=False).head(10)
        
        fig = px.bar(
            x=channel_activity.values,
            y=channel_activity.index,
            orientation='h',
            title="Top 10 Channels by Total Mentions",
            labels={'x': 'Total Mentions', 'y': 'Channel'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Video content table
    st.subheader("📋 Video Content Details")
    display_columns = ['video_title', 'channel_title_clean', 'artist_name', 'total_artist_mentions']
    available_columns = [col for col in display_columns if col in video_context_data.columns]
    
    if available_columns:
        # Add search functionality
        search_term = st.text_input("🔍 Search videos:", placeholder="Search by title, channel, or artist...")
        
        display_data = video_context_data.copy()
        if search_term:
            mask = False
            for col in available_columns:
                if col in display_data.columns:
                    mask |= display_data[col].astype(str).str.contains(search_term, case=False, na=False)
            display_data = display_data[mask]
        
        st.dataframe(
            display_data[available_columns].head(20),
            use_container_width=True,
            hide_index=True
        )
        
        if len(display_data) > 20:
            st.info(f"Showing top 20 of {len(display_data)} videos")
    else:
        st.warning("Video data structure is not as expected")

def sentiment_deep_dive_page(artist_sentiment_data):
    """Render the sentiment deep dive page"""
    st.header("💭 Sentiment Deep Dive")

    # Add explanation of what this page shows
    with st.expander("ℹ️ What does this analysis show?", expanded=False):
        st.markdown("""
        This page provides **detailed sentiment analysis** of Japanese music artist discussions across platforms.
        
        **Key Metrics:**
        - **Sentiment Distribution**: How positive, negative, or neutral discussions are
        - **Artist-Specific Sentiment**: Individual sentiment scores for each artist
        - **Community Health**: Overall sentiment health of the music community
        - **Sentiment Trends**: Changes in public perception over time
        
        **What this tells us:**
        - Which artists have the most positive/negative reception
        - Overall mood and sentiment in Japanese music communities
        - Potential issues or celebrations in the music scene
        """)

    if not artist_sentiment_data.empty:
        # Sentiment overview
        col1, col2, col3 = st.columns(3)

        total_mentions = artist_sentiment_data['mention_count'].sum()
        avg_sentiment_score = artist_sentiment_data['avg_sentiment_score'].mean()

        # Calculate sentiment distribution
        positive_artists = len(artist_sentiment_data[artist_sentiment_data['overall_sentiment'] == 'positive'])
        negative_artists = len(artist_sentiment_data[artist_sentiment_data['overall_sentiment'] == 'negative'])
        neutral_artists = len(artist_sentiment_data[artist_sentiment_data['overall_sentiment'] == 'neutral'])
        total_artists = len(artist_sentiment_data)

        with col1:
            st.metric("Total Mentions", f"{total_mentions:,}")
        with col2:
            st.metric("Average Sentiment Score", f"{avg_sentiment_score:.2f}/10")
        with col3:
            if total_artists > 0:
                positive_pct = (positive_artists / total_artists) * 100
                st.metric("Positive Sentiment %", f"{positive_pct:.1f}%")

        st.markdown("---")

        # Sentiment Insights
        st.subheader("📊 Sentiment Insights")

        col1, col2 = st.columns(2)

        with col1:
            # Create sentiment distribution pie chart
            fig = create_sentiment_distribution_chart(artist_sentiment_data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Health score calculation and display
            if total_artists > 0:
                health_score = ((positive_artists * 100) + (neutral_artists * 50)) / total_artists
                st.markdown("### 🏥 Sentiment Health Score")
                st.markdown(f"**{health_score:.1f}/100**")

                if health_score >= 75:
                    st.success("🟢 Excellent sentiment health")
                elif health_score >= 50:
                    st.warning("🟡 Moderate sentiment health")
                else:
                    st.error("🔴 Poor sentiment health")

                # Percentage breakdown
                st.markdown("### 📈 Breakdown")
                st.markdown(f"- **Positive:** {positive_artists} artists ({(positive_artists/total_artists)*100:.1f}%)")
                st.markdown(f"- **Neutral:** {neutral_artists} artists ({(neutral_artists/total_artists)*100:.1f}%)")
                st.markdown(f"- **Negative:** {negative_artists} artists ({(negative_artists/total_artists)*100:.1f}%)")

        # Top positive and negative artists
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🌟 Most Positive Artists")
            positive_artists_df = artist_sentiment_data[
                artist_sentiment_data['overall_sentiment'] == 'positive'
            ].nlargest(5, 'avg_sentiment_score')

            if not positive_artists_df.empty:
                for _, artist in positive_artists_df.iterrows():
                    st.markdown(f"**{artist['artist_name']}** - {artist['avg_sentiment_score']:.2f}/10 ({artist['mention_count']} mentions)")
            else:
                st.info("No positive sentiment artists found")

        with col2:
            st.subheader("⚠️ Most Negative Artists")
            negative_artists_df = artist_sentiment_data[
                artist_sentiment_data['overall_sentiment'] == 'negative'
            ].nsmallest(5, 'avg_sentiment_score')

            if not negative_artists_df.empty:
                for _, artist in negative_artists_df.iterrows():
                    st.markdown(f"**{artist['artist_name']}** - {artist['avg_sentiment_score']:.2f}/10 ({artist['mention_count']} mentions)")
            else:
                st.info("No negative sentiment artists found")

    else:
        st.warning("No sentiment data available")

def ai_trend_summary_page(trend_summary_data):
    """Render the AI trend summary page"""
    st.header("📈 AI-Generated Trend Summary")

    # Add explanation of what this page shows
    with st.expander("ℹ️ What does this analysis show?", expanded=False):
        st.markdown("""
        This page presents **AI-generated insights** and **trend analysis** of Japanese music discussions.
        
        **AI-Powered Features:**
        - **Automated Trend Detection**: AI identifies emerging patterns and trends
        - **Genre Popularity Analysis**: Machine learning-based genre trend scoring
        - **Sentiment Patterns**: AI analysis of community mood and reactions
        - **Engagement Classification**: Automated categorization of discussion activity levels
        
        **What this tells us:**
        - Emerging trends that might not be immediately obvious
        - AI-detected patterns in genre popularity and artist momentum
        - Automated insights into community sentiment shifts
        - Data-driven trend predictions and analysis
        """)

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

def ai_insights_page(insights_summary_data):
    """Render the AI-generated music insights page"""
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
                from urllib.parse import unquote
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

            if search_term and search_term.strip():
                # Search in both artist names and insight text (case insensitive)
                # Use regex=False to treat search term as literal string, not regex
                mask = (
                    artist_insights['artist_name'].str.contains(search_term, case=False, na=False, regex=False) |
                    artist_insights['insight_text'].str.contains(search_term, case=False, na=False, regex=False)
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
                if search_term and search_term.strip():
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
                    if not search_term or not search_term.strip():
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
                                if search_term and search_term.strip() and view_mode == "Search Results":
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

def content_discovery_page(enriched_artist_data, url_analysis_data):
    """Render the content discovery page with enriched data"""
    st.header("🔍 Content Discovery & Source Analysis")
    
    # Add explanation of what this page shows
    with st.expander("ℹ️ What does this analysis show?", expanded=False):
        st.markdown("""
        This page analyzes **content sources** and **cross-platform presence** of Japanese music artists.
        
        **Key Features:**
        - **Cross-Platform Analysis**: How artists perform across YouTube and Reddit
        - **Content Volume**: Number of unique videos, posts, channels, and subreddits
        - **URL Patterns**: Most linked content and external references
        - **Source Distribution**: Where music discussions originate and spread
        
        **What this tells us:**
        - Which artists have the strongest cross-platform presence
        - Content hotspots and influential channels/communities
        - How music content spreads across different platforms
        - Popular external links and resources in music discussions
        """)
    
    if not enriched_artist_data.empty:
        # Overview metrics
        st.subheader("📊 Content Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_videos = enriched_artist_data['unique_videos_mentioned'].sum()
            st.metric("YouTube Videos", f"{int(total_videos):,}")
        with col2:
            total_posts = enriched_artist_data['unique_posts_mentioned'].sum()
            st.metric("Reddit Posts", f"{int(total_posts):,}")
        with col3:
            total_channels = enriched_artist_data['unique_channels'].sum()
            st.metric("YouTube Channels", f"{int(total_channels):,}")
        with col4:
            total_subreddits = enriched_artist_data['unique_subreddits'].sum()
            st.metric("Subreddits", f"{int(total_subreddits):,}")
        
        st.markdown("---")
        
        # Artist content analysis
        st.subheader("🎤 Artist Content Distribution")
        
        # Filter to top artists with content
        top_content_artists = enriched_artist_data.nlargest(15, 'total_mentions')
        
        col1, col2 = st.columns(2)
        
        with col1:
            # YouTube content chart
            fig = px.scatter(top_content_artists,
                           x='youtube_mentions',
                           y='unique_videos_mentioned',
                           size='total_mentions',
                           color='unique_channels',
                           hover_name='artist_name',
                           title="YouTube Content: Mentions vs Videos",
                           labels={'youtube_mentions': 'YouTube Mentions',
                                  'unique_videos_mentioned': 'Unique Videos'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Reddit content chart
            fig = px.scatter(top_content_artists,
                           x='reddit_mentions',
                           y='unique_posts_mentioned',
                           size='total_mentions',
                           color='unique_subreddits',
                           hover_name='artist_name',
                           title="Reddit Content: Mentions vs Posts",
                           labels={'reddit_mentions': 'Reddit Mentions',
                                  'unique_posts_mentioned': 'Unique Posts'})
            st.plotly_chart(fig, use_container_width=True)
        
        # Platform comparison
        st.subheader("📱 Platform Presence Comparison")
        platform_comparison = top_content_artists[
            ['artist_name', 'youtube_mentions', 'reddit_mentions', 'mentions_with_urls']
        ].copy()
        
        fig = px.bar(platform_comparison,
                    x='artist_name',
                    y=['youtube_mentions', 'reddit_mentions', 'mentions_with_urls'],
                    title="Artist Mentions by Platform",
                    barmode='group')
        fig.update_layout(height=400)
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
        
    if not url_analysis_data.empty:
        st.subheader("🔗 URL Analysis & Content Links") 
        
        # URL category distribution
        col1, col2 = st.columns(2)
        
        with col1:
            url_categories = url_analysis_data['url_category'].value_counts()
            fig = px.pie(values=url_categories.values,
                        names=url_categories.index,
                        title="URL Categories Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top artists by URL mentions
            top_url_artists = url_analysis_data.nlargest(10, 'mention_count')
            fig = px.bar(top_url_artists,
                        x='mention_count',
                        y='artist_name',
                        orientation='h',
                        title="Artists Most Linked in Content",
                        color='avg_confidence')
            st.plotly_chart(fig, use_container_width=True)
        
        # URL patterns table
        st.subheader("📋 Popular Content Links")
        display_urls = url_analysis_data[
            ['artist_name', 'url_category', 'mention_count', 'avg_confidence', 'sample_urls']
        ].head(20)
        
        # Clean up the display
        display_urls = display_urls.copy()
        display_urls['avg_confidence'] = display_urls['avg_confidence'].round(3)
        display_urls.columns = ['Artist', 'URL Category', 'Mentions', 'Confidence', 'Sample URLs']
        
        st.dataframe(display_urls, use_container_width=True)
    
    if enriched_artist_data.empty and url_analysis_data.empty:
        st.warning("No enriched content data available")

def author_influence_page(author_influence_data):
    """Render the author influence analysis page"""
    st.header("👥 Author Influence & Community Analysis")
    
    # Add explanation of what this page shows
    with st.expander("ℹ️ What does this analysis show?", expanded=False):
        st.markdown("""
        This page analyzes **community members** and their **influence** in Japanese music discussions.
        
        **Key Metrics:**
        - **Influence Score**: Calculated based on mentions, artist diversity, and activity patterns
        - **Cross-Platform Activity**: Authors active on multiple platforms (Reddit + YouTube)
        - **Community Categories**: High/Medium/Low influence classification
        - **Activity Patterns**: Frequency and consistency of participation
        
        **What this tells us:**
        - Who are the most influential voices in Japanese music communities
        - Cross-platform influencers who bridge different communities
        - Activity patterns of engaged community members
        - Distribution of influence across platforms
        """)
    
    if not author_influence_data.empty:
        # Overview metrics
        st.subheader("📊 Community Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_authors = len(author_influence_data)
            st.metric("Active Authors", f"{total_authors:,}")
        with col2:
            high_influence = len(author_influence_data[
                author_influence_data['influence_category'] == 'High Influence'
            ])
            st.metric("High Influence", f"{high_influence}")
        with col3:
            avg_influence = author_influence_data['influence_score'].mean()
            st.metric("Avg Influence Score", f"{avg_influence:.1f}")
        with col4:
            cross_platform = len(author_influence_data[
                author_influence_data['unique_sources'] > 1
            ])
            st.metric("Cross-Platform Users", f"{cross_platform}")
        
        st.markdown("---")
        
        # Influence distribution
        st.subheader("🏆 Influence Distribution")
        col1, col2 = st.columns(2)
        
        with col1:
            # Influence category pie chart
            influence_dist = author_influence_data['influence_category'].value_counts()
            fig = px.pie(values=influence_dist.values,
                        names=influence_dist.index,
                        title="Author Influence Categories",
                        color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Platform distribution
            platform_dist = author_influence_data['platform'].value_counts()
            fig = px.bar(x=platform_dist.index,
                        y=platform_dist.values,
                        title="Authors by Platform",
                        color=platform_dist.values,
                        color_continuous_scale='viridis')
            st.plotly_chart(fig, use_container_width=True)
        
        # Top influencers
        st.subheader("🌟 Top Influencers")
        
        # Filter and display top influencers
        top_influencers = author_influence_data.nlargest(20, 'influence_score')
        
        fig = px.scatter(top_influencers,
                        x='total_mentions',
                        y='influence_score',
                        size='unique_artists_mentioned',
                        color='platform',
                        hover_name='author_name',
                        title="Influence Score vs Total Mentions",
                        labels={'total_mentions': 'Total Mentions',
                               'influence_score': 'Influence Score'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed influencers table
        st.subheader("📋 Top Influencers Details")
        
        display_influencers = top_influencers[[
            'author_name', 'platform', 'total_mentions', 'unique_artists_mentioned',
            'influence_score', 'influence_category', 'mentions_per_day'
        ]].copy()
        display_influencers.columns = [
            'Author', 'Platform', 'Total Mentions', 'Artists Mentioned',
            'Influence Score', 'Category', 'Mentions/Day'
        ]
        display_influencers['Influence Score'] = display_influencers['Influence Score'].round(1)
        display_influencers['Mentions/Day'] = display_influencers['Mentions/Day'].round(2)
        
        st.dataframe(display_influencers, use_container_width=True)
        
        # Activity patterns
        st.subheader("📈 Activity Patterns")
        col1, col2 = st.columns(2)
        
        with col1:
            # Activity vs influence
            fig = px.scatter(author_influence_data.sample(min(100, len(author_influence_data))),
                           x='activity_days',
                           y='mentions_per_day',
                           color='influence_score',
                           title="Activity Pattern: Days vs Mentions/Day",
                           color_continuous_scale='viridis')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Cross-platform analysis
            cross_platform_data = author_influence_data[
                author_influence_data['unique_sources'] > 1
            ].nlargest(15, 'influence_score')
            
            if not cross_platform_data.empty:
                fig = px.bar(cross_platform_data,
                           x='unique_sources',
                           y='author_name',
                           orientation='h',
                           title="Cross-Platform Authors",
                           color='influence_score')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No cross-platform authors found")
    
    else:
        st.warning("No author influence data available")

def video_context_page(video_context_data):
    """Render the video context analysis page"""
    st.header("🎬 Video Context & Engagement Analysis")
    
    # Add explanation of what this page shows
    with st.expander("ℹ️ What does this analysis show?", expanded=False):
        st.markdown("""
        This page analyzes **YouTube videos** where **Japanese music artists** are frequently discussed in the comments.
        
        **Key Metrics Explained:**
        - **Artist Mentions**: How many times artists are mentioned in video comments
        - **Mention %**: Percentage of comments that mention artists (higher % = more music-focused discussion)
        - **Views**: Total YouTube view count for the video
        - **Unique Artists**: Number of different artists mentioned in the video's comments
        
        **What this tells us:**
        - Which videos generate the most discussion about Japanese music artists
        - How engaged audiences are with music content across different channels
        - Trending videos that are driving music conversations
        """)

    if not video_context_data.empty:
        # Overview metrics
        st.subheader("📊 Video Content Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_videos = len(video_context_data)
            st.metric("Videos Analyzed", f"{total_videos:,}")
        with col2:
            avg_mentions = video_context_data['total_artist_mentions'].mean()
            st.metric("Avg Artist Mentions", f"{avg_mentions:.1f}")
        with col3:
            total_views = video_context_data['view_count'].sum()
            st.metric("Total Views", f"{total_views:,}")
        with col4:
            avg_engagement = video_context_data['artist_mention_percentage'].mean()
            st.metric("Avg Mention %", f"{avg_engagement:.1f}%")
        
        st.markdown("---")
        
        # Video performance analysis
        st.subheader("🚀 High-Performance Videos")
        
        # Top videos by artist mentions
        top_videos = video_context_data.nlargest(15, 'total_artist_mentions')
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Artist mentions vs views
            fig = px.scatter(top_videos,
                           x='view_count',
                           y='total_artist_mentions',
                           size='artist_mention_percentage',
                           color='unique_artists_mentioned',
                           hover_name='video_title',
                           title="Views vs Artist Mentions",
                           labels={'view_count': 'View Count',
                                  'total_artist_mentions': 'Artist Mentions'})
            fig.update_layout(xaxis_type="log")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Engagement percentage distribution
            fig = px.histogram(video_context_data,
                             x='artist_mention_percentage',
                             nbins=20,
                             title="Distribution of Artist Mention Percentages",
                             labels={'artist_mention_percentage': 'Artist Mention %'})
            st.plotly_chart(fig, use_container_width=True)
        
        # Channel analysis
        st.subheader("📺 Channel Performance")
        
        # Top channels by artist discussion
        channel_stats = video_context_data.groupby('channel_title_clean').agg({
            'total_artist_mentions': 'sum',
            'unique_artists_mentioned': 'mean',
            'view_count': 'sum',
            'video_id': 'count'
        }).reset_index()
        channel_stats.columns = ['channel', 'total_mentions', 'avg_artists_per_video', 'total_views', 'video_count']
        channel_stats = channel_stats.nlargest(15, 'total_mentions')
        
        fig = px.bar(channel_stats,
                    x='total_mentions',
                    y='channel',
                    orientation='h',
                    title="Channels with Most Artist Discussions",
                    color='avg_artists_per_video',
                    color_continuous_scale='viridis')
        st.plotly_chart(fig, use_container_width=True)
        
        # Video details table
        st.subheader("📋 Top Videos with Artist Discussions")
        
        # Add column headers with explanations
        st.markdown("##### Video Performance Metrics")
        header_col1, header_col2, header_col3, header_col4, header_col5 = st.columns([3, 0.7, 0.7, 0.9, 0.4])
        
        with header_col1:
            st.markdown("**📺 Video Title & Channel**")
        with header_col2:
            st.markdown("**🎤 Artist Mentions**", help="Total number of times artists are mentioned in comments")
        with header_col3:
            st.markdown("**📊 Mention %**", help="Percentage of comments that mention artists (Artist Mentions ÷ Total Comments)")
        with header_col4:
            st.markdown("**👁️ Views**", help="Total video view count on YouTube")
        with header_col5:
            st.markdown("**▶️ Watch**")
        
        st.markdown("---")
        
        # Display videos using a very compact layout
        video_container = st.container()
        with video_container:
            for i, (_, video) in enumerate(top_videos.iterrows()):
                # Create a compact single-line layout
                col1, col2, col3, col4, col5 = st.columns([3, 0.7, 0.7, 0.9, 0.4])
                
                with col1:
                    # Truncate title for single line display
                    video_title = video['video_title']
                    if len(video_title) > 70:
                        video_title = video_title[:70] + "..."
                    
                    # Single line with title and channel
                    channel_name = video['channel_title_clean'][:25] + "..." if len(video['channel_title_clean']) > 25 else video['channel_title_clean']
                    st.markdown(f"**[{video_title}]({video['video_url']})** • 📺 {channel_name}")
                
                with col2:
                    mentions = int(video['total_artist_mentions'])
                    st.markdown(f"🎤 **{mentions}**", help=f"{mentions} artist mentions found in comments")
                
                with col3:
                    percentage = float(video['artist_mention_percentage'])
                    st.markdown(f"📊 **{percentage:.1f}%**", help=f"{percentage:.1f}% of comments mention artists")
                
                with col4:
                    views = int(video['view_count'])
                    st.markdown(f"👁️ **{views:,}**", help=f"{views:,} total views on YouTube")
                
                with col5:
                    st.link_button("▶️", video['video_url'], help="Watch video on YouTube")
                
                # Only add minimal spacing between rows (no dividers)
                if i < len(top_videos) - 1:
                    st.write("")  # Just a small space
        
        # Time-based analysis
        st.subheader("⏰ Temporal Patterns")
        
        # Convert published_at to datetime if it's not already
        if 'video_published_at' in video_context_data.columns:
            video_context_data['video_published_at'] = pd.to_datetime(video_context_data['video_published_at'])
            video_context_data['publish_date'] = video_context_data['video_published_at'].dt.date
            
            # Daily artist mentions in videos
            daily_stats = video_context_data.groupby('publish_date').agg({
                'total_artist_mentions': 'sum',
                'video_id': 'count'
            }).reset_index()
            daily_stats.columns = ['date', 'total_mentions', 'video_count']
            
            fig = px.line(daily_stats,
                         x='date',
                         y='total_mentions',
                         title="Daily Artist Mentions in Videos",
                         labels={'date': 'Date', 'total_mentions': 'Total Mentions'})
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.warning("No video context data available")

def get_lucky_page():
    """Random artist discovery page"""
    st.header("🎲 Get Lucky - Random Artist Discovery")

    # Add explanation of what this page shows
    with st.expander("ℹ️ What is Get Lucky?", expanded=False):
        st.markdown("""
        **Get Lucky** is your gateway to **discovering Japanese music artists** you might not know about!
        
        **How it works:**
        - **Random Selection**: We randomly pick an artist from our database of Japanese music discussions
        - **Comprehensive Profile**: See everything we know about them - sentiment, mentions, rankings, genres
        - **Discovery Focus**: Perfect for finding hidden gems and lesser-known artists
        - **Full Context**: Understand where they rank among all artists and what makes them special
        
        **What you'll see:**
        - **Basic Stats**: Mentions, sentiment score, trend strength
        - **Rankings**: Where they rank compared to all other artists (e.g., #47 out of 892 artists)
        - **Genre Associations**: What genres they're associated with
        - **Platform Presence**: How they perform on YouTube vs Reddit
        - **AI Insights**: What our AI has discovered about them
        
        **Perfect for:**
        - Discovering new artists you might not know
        - Getting inspiration for music exploration  
        - Understanding lesser-known artists in the Japanese music scene
        - Finding hidden gems in specific genres or platforms
        """)

    # Refresh button
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🎲 Get Another Lucky Artist", type="primary"):
            # Clear cache to get a new random artist
            DataManager.get_random_artist_profile.clear()
            st.rerun()
    with col2:
        if st.button("🔄 Refresh Data"):
            # Clear all relevant caches
            DataManager.get_random_artist_profile.clear()
            st.rerun()

    # Load random artist profile
    with st.spinner("🎯 Finding your lucky artist..."):
        profile = DataManager.get_random_artist_profile()

    if not profile or not profile.get('basic_info'):
        st.error("😞 No artist data available. Please try again later.")
        return

    basic_info = profile['basic_info']
    artist_name = basic_info['name']

    # Artist header
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"🎤 Your Lucky Artist: **{artist_name}**")
    with col2:
        # Quick stats badge
        trend_color = "🟢" if basic_info['trend_direction'] == 'positive' else "🔴" if basic_info['trend_direction'] == 'negative' else "🟡"
        st.markdown(f"**{trend_color} {basic_info['trend_direction'].title()} Trend**")

    # Main metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Mentions",
            f"{basic_info['mention_count']:,}",
            help="Total mentions across all platforms"
        )
    
    with col2:
        sentiment_delta = f"+{basic_info['sentiment_score']:.1f}" if basic_info['sentiment_score'] > 5.0 else f"{basic_info['sentiment_score']:.1f}"
        st.metric(
            "Sentiment Score",
            f"{basic_info['sentiment_score']:.1f}/10",
            delta=sentiment_delta,
            help="Average sentiment score (5.0 = neutral, >5.0 = positive)"
        )
    
    with col3:
        st.metric(
            "Trend Strength",
            f"{basic_info['trend_strength']:.2f}",
            help="How strongly they're trending"
        )
    
    with col4:
        st.metric(
            "Engagement Level",
            basic_info['engagement_level'].title(),
            help="Overall engagement classification"
        )

    # Rankings section
    if profile.get('rankings'):
        rankings = profile['rankings']
        st.markdown("---")
        st.subheader("📊 Artist Rankings")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Mention Rank",
                f"#{rankings['mention_rank']:,}",
                delta=f"of {rankings['total_artists']:,} artists",
                help=f"Ranked #{rankings['mention_rank']} out of {rankings['total_artists']} artists by total mentions"
            )
        
        with col2:
            st.metric(
                "Sentiment Rank", 
                f"#{rankings['sentiment_rank']:,}",
                delta=f"of {rankings['total_artists']:,} artists",
                help=f"Ranked #{rankings['sentiment_rank']} out of {rankings['total_artists']} artists by sentiment score"
            )
        
        with col3:
            st.metric(
                "Trend Rank",
                f"#{rankings['trend_rank']:,}",
                delta=f"of {rankings['total_artists']:,} artists", 
                help=f"Ranked #{rankings['trend_rank']} out of {rankings['total_artists']} artists by trend strength"
            )
        
        with col4:
            st.metric(
                "Platform Rank",
                f"#{rankings['platform_rank']:,}",
                delta=f"of {rankings['total_artists']:,} artists",
                help=f"Ranked #{rankings['platform_rank']} out of {rankings['total_artists']} artists by platform presence"
            )

    # Create tabs for detailed information
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎵 Genres", "📱 Platform Presence", "💭 Sentiment Details", "🤖 AI Insights", "🎥 YouTube Videos"])
    
    with tab1:
        st.subheader("🎵 Associated Genres")
        genres = profile.get('genres', [])
        if genres:
            # Display genres as badges
            genre_cols = st.columns(min(len(genres), 5))
            for i, genre in enumerate(genres):
                with genre_cols[i % 5]:
                    st.markdown(f"**🎶 {genre}**")
            
            if len(genres) > 5:
                st.info(f"Showing top 5 of {len(genres)} associated genres")
        else:
            st.info(f"No genre associations found for {artist_name}")
    
    with tab2:
        st.subheader("📱 Platform Presence")
        platforms = profile.get('platforms', {})
        if platforms:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📺 YouTube Presence**")
                st.metric("YouTube Mentions", f"{platforms.get('youtube_mentions', 0):,}")
                st.metric("Unique Videos", f"{platforms.get('unique_videos', 0):,}")
                st.metric("Unique Channels", f"{platforms.get('unique_channels', 0):,}")
            
            with col2:
                st.markdown("**🟠 Reddit Presence**")
                st.metric("Reddit Mentions", f"{platforms.get('reddit_mentions', 0):,}")
                st.metric("Unique Posts", f"{platforms.get('unique_posts', 0):,}")
                st.metric("Unique Subreddits", f"{platforms.get('unique_subreddits', 0):,}")
            
            # Platform distribution chart
            if platforms.get('youtube_mentions', 0) > 0 or platforms.get('reddit_mentions', 0) > 0:
                st.markdown("**Platform Distribution**")
                platform_data = pd.DataFrame({
                    'Platform': ['YouTube', 'Reddit'],
                    'Mentions': [platforms.get('youtube_mentions', 0), platforms.get('reddit_mentions', 0)]
                })
                
                fig = px.pie(platform_data, values='Mentions', names='Platform', 
                           title=f"{artist_name} - Platform Distribution")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No detailed platform data available for {artist_name}")
    
    with tab3:
        st.subheader("💭 Sentiment Analysis")
        sentiment_details = profile.get('sentiment_details', {})
        if sentiment_details:
            col1, col2 = st.columns(2)
            
            with col1:
                overall_sentiment = sentiment_details.get('overall_sentiment', 'unknown')
                sentiment_emoji = "😊" if overall_sentiment == 'positive' else "😞" if overall_sentiment == 'negative' else "😐"
                st.markdown(f"**Overall Sentiment: {sentiment_emoji} {overall_sentiment.title()}**")
                st.metric("Sentiment Score", f"{sentiment_details.get('sentiment_score', 0):.2f}/10")
                st.metric("Sentiment Mentions", f"{sentiment_details.get('mention_count', 0):,}")
            
            with col2:
                # Sentiment gauge visualization
                sentiment_score = sentiment_details.get('sentiment_score', 5.0)
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = sentiment_score,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Sentiment Score"},
                    gauge = {
                        'axis': {'range': [None, 10]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 3], 'color': "lightcoral"},
                            {'range': [3, 7], 'color': "lightyellow"}, 
                            {'range': [7, 10], 'color': "lightgreen"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 5.0
                        }
                    }
                ))
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No detailed sentiment data available for {artist_name}")
    
    with tab4:
        st.subheader("🤖 AI-Generated Insights")
        ai_insights = profile.get('ai_insights', [])
        if ai_insights:
            for i, insight in enumerate(ai_insights, 1):
                with st.expander(f"💡 AI Insight #{i}"):
                    st.write(insight)
        else:
            st.info(f"No AI insights available for {artist_name} yet.")
            st.markdown("*AI insights are generated based on discussion patterns and community engagement.*")

    with tab5:
        try:
            from get_lucky_youtube_patch import add_youtube_section_to_get_lucky
            add_youtube_section_to_get_lucky(artist_name)
        except ImportError:
            st.warning("YouTube integration not available")
            # Provide manual search as fallback
            search_url = f"https://www.youtube.com/results?search_query={artist_name.replace(' ', '+')}"
            st.markdown(f"🔍 **[Search for {artist_name} on YouTube]({search_url})**")

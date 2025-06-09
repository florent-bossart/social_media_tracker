"""
Dashboard Pages module for the Japanese Music Trends Dashboard.
Contains the logic for each individual page/section of the dashboard.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from visualizations import (
    create_artist_trends_chart, create_genre_radar_chart,
    create_genre_artist_diversity_chart, create_wordcloud_chart,
    create_platform_comparison, create_temporal_trends,
    create_artist_bar_chart, create_sentiment_distribution_chart
)
from ui_components import (
    display_metrics_row, display_top_artists_sidebar,
    display_temporal_summary, display_trend_summary_overview,
    display_artist_details
)

def overview_page(stats, artist_data, temporal_data, trend_summary_data):
    """Render the overview page"""
    st.header("🌟 Music Social Media Landscape")

    # Key metrics row
    display_metrics_row(stats)
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
        display_top_artists_sidebar(artist_data)

    # Temporal overview
    display_temporal_summary(temporal_data)

    # Show the temporal chart
    if not temporal_data.empty:
        fig = create_temporal_trends(temporal_data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    # Trend summary overview
    display_trend_summary_overview(trend_summary_data)

def artist_trends_page(artist_data, platform_data):
    """Render the artist trends page"""
    st.header("🎤 Artist Deep Dive")

    if not artist_data.empty:
        # Artist selector
        selected_artist = st.selectbox("Select an artist for detailed analysis:", artist_data['artist_name'].tolist())
        artist_info = artist_data[artist_data['artist_name'] == selected_artist].iloc[0]

        # Artist overview
        display_artist_details(artist_info)

        # Artist comparison chart
        st.subheader("📊 Artist Comparison")
        fig = create_artist_bar_chart(artist_data, "Artist Mentions with Sentiment Coloring")
        if fig:
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

def genre_analysis_page(genre_data, genre_artist_diversity_data, artists_without_genre_count):
    """Render the genre analysis page"""
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

        # Genre sentiment comparison
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

def platform_insights_page(platform_data):
    """Render the platform insights page"""
    st.header("📱 Platform Insights & Comparison")

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

def sentiment_deep_dive_page(artist_sentiment_data):
    """Render the sentiment deep dive page"""
    st.header("💭 Sentiment Deep Dive")

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
    """Render the AI insights page"""
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

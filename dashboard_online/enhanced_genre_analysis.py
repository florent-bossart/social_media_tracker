"""
Enhanced Genre Analysis Page with genre selection and artist exploration.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from ui_library import StandardComponents, StandardCharts, UITheme
from data_manager import DataManager
from visualizations import create_genre_radar_chart, create_genre_artist_diversity_chart

def enhanced_genre_analysis_page():
    """Enhanced genre analysis page with genre selection and artist discovery"""

    # Page header
    StandardComponents.page_header(
        title="Genre Analysis & Artist Discovery",
        icon="🎶",
        description="""
        **Comprehensive Genre Intelligence** - Explore Japanese music genres and discover associated artists.

        **What you can do:**
        - **Browse Genres**: View trending genres and their performance metrics
        - **Select a Genre**: Click on any genre to see all associated artists
        - **Discover Artists**: Explore which artists are popular in each genre
        - **Export Data**: Download complete artist lists for any genre
        - **Compare Metrics**: Analyze sentiment, mentions, and platform presence
        """
    )

    # Load genre data
    with st.spinner("Loading genre analysis data..."):
        genre_data = DataManager.get_genre_trends()
        genre_artist_diversity_data = DataManager.get_genre_artists()
        try:
            artists_without_genre_count = DataManager.get_artists_without_genre_count()
        except:
            artists_without_genre_count = None

    if genre_data.empty:
        StandardComponents.empty_state(
            "No Genre Data Available",
            "Genre analysis data is currently being processed. Please check back later.",
            "🎶"
        )
        return

    # Genre Performance Overview
    st.subheader("🎵 Genre Performance Overview")

    # Create two columns for genre overview
    col1, col2 = st.columns([2, 1])

    with col1:
        # Genre radar chart
        fig = create_genre_radar_chart(genre_data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Display top genres with key metrics
        st.subheader("🔥 Top Genres")
        for i, (_, genre) in enumerate(genre_data.head(5).iterrows()):
            with st.container():
                st.write(f"**{genre['genre']}**")
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.caption(f"Mentions: {int(genre['mention_count'])}")
                with col_b:
                    st.caption(f"Sentiment: {genre['sentiment_score']:.1f}")
                with col_c:
                    st.caption(f"Trend: {genre['trend_strength']:.2f}")
                st.markdown("<br>", unsafe_allow_html=True)

    # Genre sentiment analysis
    st.subheader("📊 Genre Sentiment Analysis")
    fig = px.bar(genre_data,
                 x='genre',
                 y='sentiment_score',
                 color='sentiment_score',
                 title="Sentiment Score by Genre",
                 color_continuous_scale='RdYlGn',
                 hover_data=['mention_count', 'trend_strength'])
    fig.update_layout(height=400)
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

    # Genre Selection Section - moved below sentiment analysis
    st.markdown("---")
    st.subheader("🎯 Genre Selection & Artist Discovery")

    # Genre selector with session state
    if not genre_data.empty:
        # Create a genre list with metrics
        genre_options = ["Select a genre..."] + genre_data['genre'].tolist()
        
        if 'selected_genre' not in st.session_state:
            st.session_state.selected_genre = "Select a genre..."
            
        selected_genre = st.selectbox(
            "Choose a genre to explore artists:",
            genre_options,
            index=genre_options.index(st.session_state.selected_genre) if st.session_state.selected_genre in genre_options else 0,
            help="Select any genre to see all artists associated with it",
            key="genre_selector"
        )
        
        st.session_state.selected_genre = selected_genre

    # Genre-specific artist analysis
    if selected_genre and selected_genre != "Select a genre...":
        st.markdown("---")
        st.subheader(f"🎤 Artists in {selected_genre}")

        # Load artists for the selected genre
        with st.spinner(f"Loading artists for {selected_genre}..."):
            genre_artists = DataManager.get_genre_artists(selected_genre)

        if not genre_artists.empty:
            # Create view selector for different views
            genre_view_key = f"genre_view_{selected_genre}"
            if genre_view_key not in st.session_state:
                st.session_state[genre_view_key] = "📊 Artist Overview"
                
            genre_view_options = ["📊 Artist Overview", "📈 Detailed Analysis", "💾 Export Data"]
            genre_view = st.selectbox(
                "Select view:",
                genre_view_options,
                index=genre_view_options.index(st.session_state[genre_view_key]),
                key=f"genre_view_select_{selected_genre}"
            )
            
            st.session_state[genre_view_key] = genre_view
            
            st.markdown("---")

            if genre_view == "📊 Artist Overview":
                # Artist metrics overview
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Artists", len(genre_artists))
                with col2:
                    avg_sentiment = genre_artists['sentiment_score'].mean()
                    st.metric("Average Sentiment", f"{avg_sentiment:.1f}/10")
                with col3:
                    total_mentions = genre_artists['mention_count'].sum()
                    st.metric("Total Mentions", f"{total_mentions:,}")

                # Top artists in the genre
                st.subheader(f"🏆 Top 20 Artists in {selected_genre}")
                top_artists = genre_artists.head(20)

                # Create a bar chart of top artists
                fig = px.bar(
                    top_artists,
                    x='mention_count',
                    y='artist_name',
                    orientation='h',
                    color='sentiment_score',
                    color_continuous_scale='RdYlGn',
                    title=f"Top Artists in {selected_genre} by Mentions",
                    hover_data=['platform_count', 'avg_confidence']
                )
                fig.update_layout(height=600, yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)

            elif genre_view == "📈 Detailed Analysis":
                # Detailed artist analysis
                st.subheader("🔍 Detailed Artist Analysis")

                # Artist selection for detailed view
                artist_options = ["Select an artist..."] + genre_artists['artist_name'].tolist()
                
                artist_select_key = f"selected_artist_{selected_genre}"
                if artist_select_key not in st.session_state:
                    st.session_state[artist_select_key] = "Select an artist..."
                    
                selected_artist = st.selectbox(
                    "Choose an artist for detailed analysis:",
                    artist_options,
                    index=artist_options.index(st.session_state[artist_select_key]) if st.session_state[artist_select_key] in artist_options else 0,
                    key=f"artist_select_{selected_genre}"
                )
                
                st.session_state[artist_select_key] = selected_artist

                if selected_artist and selected_artist != "Select an artist...":
                    artist_data = genre_artists[genre_artists['artist_name'] == selected_artist].iloc[0]

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Mentions in Genre", int(artist_data['mention_count']))
                        st.metric("Sentiment Score", f"{artist_data['sentiment_score']:.1f}/10")
                    with col2:
                        st.metric("Platform Count", int(artist_data['platform_count']))
                        st.metric("Genre Rank", f"#{int(artist_data['artist_rank'])}")

                # Show all artists table with search
                st.subheader("📋 All Artists in Genre")
                search_term = st.text_input("Search artists:", placeholder="Type artist name...")

                if search_term:
                    filtered_artists = genre_artists[
                        genre_artists['artist_name'].str.contains(search_term, case=False, na=False)
                    ]
                else:
                    filtered_artists = genre_artists

                # Display the dataframe
                st.dataframe(
                    filtered_artists[['artist_name', 'mention_count', 'sentiment_score', 'platform_count', 'artist_rank']],
                    use_container_width=True,
                    hide_index=True
                )

            elif genre_view == "💾 Export Data":
                # Export functionality
                st.subheader("💾 Export Artist Data")
                st.write(f"Export complete artist list for **{selected_genre}** genre")

                # Show export options
                export_format = st.radio(
                    "Choose export format:",
                    ["CSV", "JSON"],
                    horizontal=True
                )

                if export_format == "CSV":
                    csv_data = genre_artists.to_csv(index=False)
                    st.download_button(
                        label=f"📥 Download {selected_genre} Artists CSV",
                        data=csv_data,
                        file_name=f"{selected_genre.lower().replace(' ', '_')}_artists.csv",
                        mime="text/csv"
                    )
                else:
                    json_data = genre_artists.to_json(orient='records', indent=2)
                    st.download_button(
                        label=f"📥 Download {selected_genre} Artists JSON",
                        data=json_data,
                        file_name=f"{selected_genre.lower().replace(' ', '_')}_artists.json",
                        mime="application/json"
                    )

                # Preview the data to be exported
                st.subheader("📋 Export Preview")
                st.write(f"This will export **{len(genre_artists)}** artists with the following data:")
                st.dataframe(genre_artists.head(10), use_container_width=True)

        else:
            st.info(f"No artists found for {selected_genre} genre.")

    # Additional analysis sections
    st.markdown("---")
    st.subheader("🎨 Overall Artist Diversity by Genre")

    if not genre_artist_diversity_data.empty:
        # Get genre diversity summary
        genre_summary = genre_artist_diversity_data.groupby('genre_name').agg({
            'artist_name': 'count',
            'mention_count': 'sum',
            'sentiment_score': 'mean'
        }).reset_index()
        genre_summary.columns = ['genre', 'artist_count', 'total_mentions', 'avg_sentiment']
        genre_summary = genre_summary.sort_values('artist_count', ascending=False).head(15)

        # Create diversity chart
        fig = px.bar(
            genre_summary,
            x='artist_count',
            y='genre',
            orientation='h',
            color='avg_sentiment',
            color_continuous_scale='RdYlGn',
            title="Artist Diversity by Genre (Top 15)",
            hover_data=['total_mentions']
        )
        fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            max_diversity_genre = genre_summary.iloc[0]
            st.metric(
                "Most Diverse Genre",
                max_diversity_genre['genre'],
                f"{int(max_diversity_genre['artist_count'])} artists"
            )
        with col2:
            avg_diversity = genre_summary['artist_count'].mean()
            st.metric("Average Artists per Genre", f"{avg_diversity:.1f}")
        with col3:
            if artists_without_genre_count:
                st.metric("Artists Without Genre", f"{artists_without_genre_count}")

    else:
        st.info("No artist diversity data available for detailed analysis.")

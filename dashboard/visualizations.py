"""
Visualizations module for the Japanese Music Trends Dashboard.
Contains all chart creation and plotting functions.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from wordcloud import WordCloud

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

def create_artist_bar_chart(df, title="Artist Mentions", num_artists=20):
    """Create a bar chart for artist mentions with sentiment coloring"""
    if df.empty:
        st.warning("No artist data available")
        return None

    # Get top artists and ensure all names are visible
    top_artists = df.head(num_artists).copy()

    fig = px.bar(top_artists,
                 x='artist_name',
                 y='mention_count',
                 color='sentiment_score',
                 title=title,
                 color_continuous_scale='RdYlGn',
                 hover_data=['sentiment_score', 'mention_count'])

    # Improve layout for better readability
    fig.update_layout(
        height=600,  # Increased height for better visibility
        xaxis_title="Artist",
        yaxis_title="Mention Count",
        showlegend=False,
        margin=dict(l=50, r=50, t=50, b=120)  # More bottom margin for labels
    )

    # Rotate labels and ensure all are shown
    fig.update_xaxes(
        tickangle=45,
        tickmode='linear',  # Show all ticks
        title_standoff=25
    )

    # Add value labels on bars for clarity
    fig.update_traces(
        texttemplate='%{y}',
        textposition='outside'
    )

    return fig

def create_sentiment_distribution_chart(df):
    """Create a pie chart showing sentiment distribution"""
    if df.empty:
        st.warning("No sentiment data available")
        return None

    # Calculate sentiment distribution
    sentiment_counts = df['overall_sentiment'].value_counts()

    fig = px.pie(values=sentiment_counts.values,
                 names=sentiment_counts.index,
                 title="Sentiment Distribution",
                 color_discrete_map={
                     'positive': '#28a745',
                     'negative': '#dc3545',
                     'neutral': '#6c757d'
                 })

    fig.update_layout(height=400)
    return fig

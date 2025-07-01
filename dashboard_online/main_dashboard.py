# main_dashboard.py

import streamlit as st
import pandas as pd
import traceback
from data_manager import DataManager
from ui_library import (
    apply_global_styles, create_dashboard_header, Navigation,
    StandardComponents, UITheme
)
from artist_analytics_hub import artist_analytics_hub_page
from ai_intelligence_center import ai_intelligence_center_page
from enhanced_genre_analysis import enhanced_genre_analysis_page
from dashboard_pages import (
    overview_page, artist_trends_page, wordcloud_page, platform_insights_page, get_lucky_page,
    sentiment_deep_dive_page, ai_trend_summary_page, ai_insights_page,
    content_discovery_page, author_influence_page, video_context_page
)

def run_dashboard():
    # Page config is set in streamlit_app_robust.py to avoid conflicts
    apply_global_styles()
    create_dashboard_header()

    @st.cache_data
    def load_consolidated_data():
        data = {
            'stats': {}, 'artist_data': pd.DataFrame(),
            'genre_data': pd.DataFrame(), 'genre_artist_diversity_data': pd.DataFrame(),
            'artists_without_genre_count': 0, 'platform_data': pd.DataFrame(),
            'temporal_data': pd.DataFrame(), 'wordcloud_data': pd.DataFrame(),
            'video_context_data': pd.DataFrame(), 'artist_sentiment_data': pd.DataFrame(),
            'trend_summary_data': {}, 'insights_summary_data': {},
            'enriched_artist_data': pd.DataFrame(), 'url_analysis_data': pd.DataFrame(),
            'author_influence_data': pd.DataFrame()
        }
        try:
            with st.spinner("Loading dashboard data..."):
                stats = DataManager.get_overall_stats()
                if not stats:
                    st.info("🚀 Demo mode: no database connected.")
                    return data
                data['stats'] = stats
                loaders = {
                    'artist_data': DataManager.get_artist_trends,
                    'genre_data': DataManager.get_genre_trends,
                    'temporal_data': DataManager.get_temporal_data,
                    'wordcloud_data': DataManager.get_wordcloud_data,
                    'platform_data': DataManager.get_platform_data,
                    'video_context_data': DataManager.get_video_context_data,
                    'artist_sentiment_data': DataManager.get_artist_sentiment_data,
                    'trend_summary_data': DataManager.get_trend_summary_data,
                    'insights_summary_data': DataManager.get_insights_summary_data,
                    'genre_artist_diversity_data': DataManager.get_genre_artist_diversity,
                    'artists_without_genre_count': DataManager.get_artists_without_genre_count
                }
                for key, func in loaders.items():
                    try:
                        data[key] = func()
                    except Exception as e:
                        st.warning(f"{key} failed to load: {e}")
                
                # Load artist analytics data (contains enriched, url_analysis, author_influence)
                try:
                    artist_analytics = DataManager.get_artist_analytics_hub_data()
                    data['enriched_artist_data'] = artist_analytics.get('enriched', pd.DataFrame())
                    data['url_analysis_data'] = artist_analytics.get('url_analysis', pd.DataFrame())
                    data['author_influence_data'] = artist_analytics.get('author_influence', pd.DataFrame())
                except Exception as e:
                    st.warning(f"Artist analytics data failed to load: {e}")
                    
        except Exception as e:
            st.error(f"Failed to load data: {e}")
        return data

    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.last_refresh = pd.Timestamp.now()
        st.session_state.data_loaded = False

        # Clear cache on first load to ensure fresh data with column mapping fixes
        st.cache_data.clear()

    page = Navigation.create_sidebar_nav() or "🏠 Overview"

    if not st.session_state.get('data_loaded', False) or 'dashboard_data' not in st.session_state:
        with st.spinner("Loading dashboard data for this session..."):
            st.session_state.dashboard_data = load_consolidated_data()
            st.session_state.data_loaded = True

    data = st.session_state.dashboard_data

    try:
        with st.spinner(f"🔄 Switching to {page}..."):
            if page == "🏠 Overview":
                overview_page(data.get('stats', {}),
                              data.get('artist_data', pd.DataFrame()),
                              data.get('temporal_data', pd.DataFrame()))

            elif page == "🎤 Artist Trends":
                artist_trends_page(data.get('artist_data', pd.DataFrame()),
                                   data.get('platform_data', pd.DataFrame()))

            elif page == "🎤 Artist Analytics Hub":
                artist_analytics_hub_page()

            elif page == "🎶 Genre Analysis":
                enhanced_genre_analysis_page()

            elif page == "☁️ Word Cloud":
                wordcloud_page(data.get('wordcloud_data', pd.DataFrame()))

            elif page == "📱 Platform Insights":
                platform_insights_page(
                    data.get('platform_data', pd.DataFrame()),
                    data.get('video_context_data', pd.DataFrame())
                )
                
            elif page == "💭 Sentiment Deep Dive":
                sentiment_deep_dive_page(data.get('artist_sentiment_data', pd.DataFrame()))
                
            elif page == "📈 AI Trend Summary":
                ai_trend_summary_page(data.get('trend_summary_data', {}))
                
            elif page == "🔍 AI Insights":
                ai_insights_page(data.get('insights_summary_data', {}))
                
            elif page == "🔗 Content Discovery":
                content_discovery_page(data.get('enriched_artist_data', pd.DataFrame()),
                                        data.get('url_analysis_data', pd.DataFrame()))
                
            elif page == "👥 Author Influence":
                author_influence_page(data.get('author_influence_data', pd.DataFrame()))
                
            elif page == "🎬 Video Context":
                video_context_page(data.get('video_context_data', pd.DataFrame()))

            elif page == "🤖 AI Intelligence Center":
                ai_intelligence_center_page()

            elif page == "🎲 Get Lucky":
                get_lucky_page()

            else:
                st.warning(f"Page '{page}' not found. Loading overview.")
                overview_page(data.get('stats', {}),
                              data.get('artist_data', pd.DataFrame()),
                              data.get('temporal_data', pd.DataFrame()))

    except Exception as e:
        st.error(f"💥 Unexpected error in page routing: {str(e)}")
        st.code(traceback.format_exc())

    Navigation.page_footer()

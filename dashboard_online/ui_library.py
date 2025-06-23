"""
Standardized UI Components Library for Japanese Music Trends Dashboard.
Provides consistent, reusable components with unified styling.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional, Any

class UITheme:
    """Centralized theme configuration"""

    # Color palette
    PRIMARY_COLORS = {
        'red': '#ff6b6b',
        'teal': '#4ecdc4',
        'blue': '#667eea',
        'purple': '#764ba2',
        'green': '#28a745',
        'orange': '#fd7e14',
        'pink': '#e83e8c'
    }

    SENTIMENT_COLORS = {
        'positive': '#28a745',
        'negative': '#dc3545',
        'neutral': '#6c757d'
    }

    # Chart configuration
    CHART_CONFIG = {
        'height': 400,
        'template': 'plotly_white',
        'font_family': 'system-ui, -apple-system, sans-serif'
    }

class StandardComponents:
    """Reusable UI components with consistent styling"""

    @staticmethod
    def page_header(title: str, icon: str, description: str = None, show_info: bool = True):
        """Standardized page header with optional info section"""
        st.header(f"{icon} {title}")

        if description and show_info:
            with st.expander("ℹ️ What does this analysis show?", expanded=False):
                st.markdown(description)

        st.markdown("---")

    @staticmethod
    def metric_cards(metrics: Dict[str, Any], columns: int = 4):
        """Display metrics in standardized cards"""
        cols = st.columns(columns)

        for i, (label, value) in enumerate(metrics.items()):
            with cols[i % columns]:
                if isinstance(value, dict):
                    st.metric(
                        label=value.get('label', label),
                        value=value.get('value', 'N/A'),
                        delta=value.get('delta', None)
                    )
                else:
                    st.metric(label, value)

    @staticmethod
    def data_selector(df: pd.DataFrame,
                     column: str,
                     label: str,
                     multi: bool = True,
                     default_count: int = 5) -> List[str]:
        """Standardized data selector component"""
        if df.empty or column not in df.columns:
            st.warning(f"No data available for {label.lower()}")
            return []

        options = df[column].unique().tolist()

        if multi:
            default_selection = options[:default_count] if len(options) >= default_count else options
            return st.multiselect(
                label,
                options=options,
                default=default_selection
            )
        else:
            return [st.selectbox(label, options)]

    @staticmethod
    def data_table(df: pd.DataFrame,
                   title: str = None,
                   max_rows: int = 10,
                   columns: List[str] = None,
                   searchable: bool = False):
        """Standardized data table with optional search"""
        if df.empty:
            st.info(f"No data available{' for ' + title.lower() if title else ''}")
            return

        if title:
            st.subheader(title)

        display_df = df.copy()

        # Column selection
        if columns:
            available_cols = [col for col in columns if col in display_df.columns]
            if available_cols:
                display_df = display_df[available_cols]

        # Search functionality
        if searchable and not display_df.empty:
            search_term = st.text_input("🔍 Search data:", key=f"search_{title}")
            if search_term:
                mask = display_df.astype(str).apply(
                    lambda x: x.str.contains(search_term, case=False, na=False)
                ).any(axis=1)
                display_df = display_df[mask]

        # Display table
        if not display_df.empty:
            st.dataframe(
                display_df.head(max_rows),
                use_container_width=True,
                hide_index=True
            )

            if len(display_df) > max_rows:
                st.info(f"Showing top {max_rows} of {len(display_df)} rows")
        else:
            st.info("No matching data found")

    @staticmethod
    def error_display(error_msg: str, error_type: str = "warning"):
        """Standardized error display"""
        if error_type == "error":
            st.error(f"❌ {error_msg}")
        elif error_type == "warning":
            st.warning(f"⚠️ {error_msg}")
        else:
            st.info(f"ℹ️ {error_msg}")

    @staticmethod
    def loading_placeholder(message: str = "Loading data..."):
        """Standardized loading placeholder"""
        return st.empty().info(f"⏳ {message}")

    @staticmethod
    def empty_state(title: str, description: str, icon: str = "📊"):
        """Standardized empty state display"""
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem; color: #6c757d;">
            <h2>{icon}</h2>
            <h4>{title}</h4>
            <p>{description}</p>
        </div>
        """, unsafe_allow_html=True)

class StandardCharts:
    """Standardized chart components with consistent styling"""

    @staticmethod
    def create_bar_chart(df: pd.DataFrame,
                        x_col: str,
                        y_col: str,
                        title: str,
                        color_col: str = None,
                        horizontal: bool = False) -> go.Figure:
        """Create standardized bar chart"""
        if df.empty:
            return None

        orientation = 'h' if horizontal else 'v'
        x_axis = y_col if horizontal else x_col
        y_axis = x_col if horizontal else y_col

        fig = px.bar(
            df.head(20),  # Limit to top 20 for readability
            x=x_axis,
            y=y_axis,
            color=color_col,
            title=title,
            orientation=orientation,
            height=UITheme.CHART_CONFIG['height'] if not horizontal else 700,  # Taller for horizontal
            template=UITheme.CHART_CONFIG['template']
        )

        # Enhanced styling for horizontal charts showing artist names
        if horizontal and x_col == 'artist_name':
            fig.update_layout(
                font_family=UITheme.CHART_CONFIG['font_family'],
                showlegend=bool(color_col),
                yaxis=dict(
                    categoryorder='total ascending',  # Sort by value
                    tickmode='linear',  # Show all ticks
                    autorange=True,
                    dtick=1  # Show every artist name
                ),
                xaxis_title="Mentions Count",
                yaxis_title="Artist",
                margin=dict(l=200, r=50, t=50, b=50)  # More left margin for artist names
            )

            # Add value labels on bars
            fig.update_traces(
                texttemplate='%{x}',
                textposition='outside',
                textfont_size=10
            )
        else:
            fig.update_layout(
                font_family=UITheme.CHART_CONFIG['font_family'],
                showlegend=bool(color_col)
            )

        return fig

    @staticmethod
    def create_line_chart(df: pd.DataFrame,
                         x_col: str,
                         y_col: str,
                         title: str,
                         color_col: str = None) -> go.Figure:
        """Create standardized line chart"""
        if df.empty:
            return None

        fig = px.line(
            df,
            x=x_col,
            y=y_col,
            color=color_col,
            title=title,
            height=UITheme.CHART_CONFIG['height'],
            template=UITheme.CHART_CONFIG['template']
        )

        fig.update_layout(
            font_family=UITheme.CHART_CONFIG['font_family']
        )

        return fig

    @staticmethod
    def create_pie_chart(df: pd.DataFrame,
                        values_col: str,
                        names_col: str,
                        title: str) -> go.Figure:
        """Create standardized pie chart"""
        if df.empty:
            return None

        fig = px.pie(
            df.head(10),  # Limit to top 10 for readability
            values=values_col,
            names=names_col,
            title=title,
            height=UITheme.CHART_CONFIG['height'],
            template=UITheme.CHART_CONFIG['template']
        )

        fig.update_layout(
            font_family=UITheme.CHART_CONFIG['font_family']
        )

        return fig

    @staticmethod
    def create_scatter_plot(df: pd.DataFrame,
                           x_col: str,
                           y_col: str,
                           title: str,
                           size_col: str = None,
                           color_col: str = None,
                           hover_data: List[str] = None) -> go.Figure:
        """Create standardized scatter plot"""
        if df.empty:
            return None

        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            size=size_col,
            color=color_col,
            title=title,
            hover_data=hover_data,
            height=UITheme.CHART_CONFIG['height'],
            template=UITheme.CHART_CONFIG['template']
        )

        fig.update_layout(
            font_family=UITheme.CHART_CONFIG['font_family']
        )

        return fig

class PageLayouts:
    """Standardized page layout patterns"""

    @staticmethod
    def two_column_layout(left_content, right_content, ratio: List[int] = [2, 1]):
        """Standard two-column layout"""
        col1, col2 = st.columns(ratio)
        with col1:
            left_content()
        with col2:
            right_content()

    @staticmethod
    def three_column_metrics(metrics: List[Dict[str, Any]]):
        """Three-column metrics layout"""
        col1, col2, col3 = st.columns(3)
        cols = [col1, col2, col3]

        for i, metric in enumerate(metrics):
            if i < len(cols):
                with cols[i]:
                    st.metric(**metric)

    @staticmethod
    def tabbed_content(tabs_config: Dict[str, callable]):
        """Standardized tabbed content layout - using selectbox for stability"""
        tab_names = list(tabs_config.keys())
        
        # Use selectbox instead of tabs for better compatibility
        selected_tab = st.selectbox(
            "Select view:",
            tab_names,
            key=f"tab_selector_{hash(str(tab_names))}"
        )
        
        # Render selected content
        if selected_tab in tabs_config:
            st.markdown("---")
            tabs_config[selected_tab]()

class Navigation:
    """Navigation and routing utilities"""

    @staticmethod
    def create_sidebar_nav() -> str:
        """Create standardized sidebar navigation"""
        st.sidebar.title("🎵 Navigation")

        # Consolidated navigation structure
        return st.sidebar.radio("Choose a section:", [
            "🏠 Overview",
            "🎤 Artist Analytics Hub",
            "🎶 Genre Analysis",
            "☁️ Word Cloud",
            "📱 Platform Insights",
            "🤖 AI Intelligence Center",
            "🎲 Get Lucky"
        ])

    @staticmethod
    def page_footer():
        """Standardized page footer"""
        st.markdown("---")
        st.markdown(
            '<div style="text-align: center; color: #6c757d; font-size: 0.8rem;">'
            '🎌 Japanese Music Trends Dashboard | Powered by DBT & Streamlit'
            '</div>',
            unsafe_allow_html=True
        )

def apply_global_styles():
    """Apply global CSS styling"""
    st.markdown("""
    <style>
        /* Main header styling */
        .main-header {
            background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }

        /* Metric card styling */
        .metric-card {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #ff6b6b;
            margin-bottom: 1rem;
        }

        /* Status indicators */
        .trend-positive { color: #28a745; font-weight: bold; }
        .trend-negative { color: #dc3545; font-weight: bold; }
        .trend-neutral { color: #6c757d; font-weight: bold; }

        /* Chart containers */
        .chart-container {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin: 1rem 0;
        }

        /* Sidebar styling */
        .sidebar .sidebar-content {
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        }

        /* Table styling */
        .dataframe {
            font-size: 0.9rem;
        }

        /* Search box styling */
        .stTextInput > div > div > input {
            border-radius: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

def create_dashboard_header():
    """Create the main dashboard header"""
    st.markdown(
        '<div class="main-header">'
        '<h1>🎌 Japanese Music Trends Dashboard</h1>'
        '<p>Social Media Analytics for J-Pop, City Pop, Anime Music & More</p>'
        '<p><strong>🚀 Powered by DBT Models</strong></p>'
        '</div>',
        unsafe_allow_html=True
    )

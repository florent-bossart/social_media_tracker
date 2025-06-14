# Japanese Music Trends Dashboard

A comprehensive Streamlit dashboard for analyzing Japanese music trends from social media data using DBT models and AI-powered insights.

## 🎯 Overview

This dashboard provides real-time analytics and insights into Japanese music trends across Reddit and YouTube platforms. It features AI-generated insights, sentiment analysis, genre exploration, and comprehensive artist analytics.

## ✨ Features

### **📊 Core Analytics**
- **Real-time Metrics**: Overall engagement statistics and key performance indicators
- **Artist Trends**: Top trending Japanese artists with sentiment and popularity metrics
- **Genre Analysis**: Comprehensive genre exploration with artist selection and export capabilities
- **Platform Insights**: Cross-platform comparison (Reddit vs YouTube) with video context analysis
- **Word Cloud Analytics**: Visual representation of trending topics and discussions

### **🤖 AI-Powered Intelligence**
- **AI Intelligence Center**: Machine learning-generated trend summaries and insights
- **Smart Search**: AI-enhanced search across insights and artist data
- **Predictive Analytics**: Data-driven forecasts and trend predictions
- **Sentiment Analysis**: Deep sentiment analysis with health scoring

### **🎤 Artist Analytics Hub**
- **Trending Artists**: Real-time popularity and mention tracking
- **Content Discovery**: Source tracking and cross-platform content analysis
- **Author Influence**: Key opinion leaders and community influencer analysis
- **Artist Comparison**: Side-by-side artist performance metrics

## 🏗️ Architecture

### **Current Dashboard Structure**

```
dashboard/
├── main_dashboard.py              # Main application entry point
├── ai_intelligence_center.py     # AI-powered insights and trends
├── artist_analytics_hub.py       # Consolidated artist analysis
├── enhanced_genre_analysis.py    # Genre selection and artist discovery
├── dashboard_pages.py            # Individual page implementations
├── data_manager.py               # Centralized data management with caching
├── ui_library.py                 # Standardized UI components and styling
├── visualizations.py             # Chart creation and plotting functions
├── database_service.py           # Database connections and queries
├── data_queries.py               # DBT model query functions
├── ui_components.py              # Legacy UI components
├── Dockerfile                    # Docker configuration
└── pyproject.toml                # Dependencies and configuration
```

### **Navigation Structure**

The dashboard is organized into 6 main sections:

1. **🏠 Overview** - High-level dashboard with key metrics and top trends
2. **🎤 Artist Analytics Hub** - Comprehensive artist analysis (5 sub-tabs)
3. **🎶 Genre Analysis** - Genre exploration with artist selection and export
4. **☁️ Word Cloud** - Visual trending topics and keyword analysis  
5. **📱 Platform Insights** - Cross-platform comparison and video context
6. **🤖 AI Intelligence Center** - AI-generated insights and trend summaries (4 sub-tabs)

## 🚀 Usage

### **Local Development**
```bash
cd dashboard
streamlit run main_dashboard.py
```

### **Docker**
```bash
docker-compose up streamlit_dashboard
```

### **Access**
- **URL**: http://localhost:8501
- **Database**: PostgreSQL with DBT transformations
- **Refresh**: Data auto-refreshes with TTL caching

## 📋 Key Components

### **Data Management (`data_manager.py`)**
- Centralized data access with `@st.cache_data` caching
- Consistent error handling and data validation
- Methods for all major dashboard sections
- TTL-based cache management for real-time updates

### **Enhanced Genre Analysis (`enhanced_genre_analysis.py`)**
- **Genre Performance Overview** with radar charts and metrics
- **Genre Selection Interface** with dropdown menu (quick buttons removed)
- **Artist Discovery** with search, filtering, and ranking
- **Export Capabilities** (CSV/JSON) for complete artist lists
- **Artist Name Normalization** to eliminate duplicates (e.g., BABYMETAL variants)

### **Artist Analytics Hub (`artist_analytics_hub.py`)**
- **5 Tabbed Interface**:
  - 🔥 Trending Artists: Real-time popularity tracking
  - 💭 Sentiment Analysis: Public perception analysis
  - 🔗 Content Discovery: Source and content context tracking
  - 👥 Author Influence: Community influencer identification
  - 📊 Artist Comparison: Cross-artist metrics comparison

### **AI Intelligence Center (`ai_intelligence_center.py`)**
- **4 Tabbed Interface**:
  - 📈 Trend Summary: AI-generated trend analysis
  - 🔍 AI Insights: Deep insights with smart search
  - 🎯 Smart Search: Enhanced search across all AI data
  - 📊 Intelligence Dashboard: Comprehensive AI metrics overview

## 🛠️ Technical Details

### **Database Integration**
- **DBT Models**: 30+ data transformation models
- **PostgreSQL**: Primary data warehouse
- **Real-time Queries**: Cached with automatic refresh
- **Data Sources**: Reddit comments, YouTube comments, video metadata

### **Key DBT Models**
- `genre_artists_dashboard`: Artist-genre relationships with normalization
- `artist_sentiment_dashboard`: Sentiment analysis by artist
- `trend_summary_top_genres_normalized`: Genre trend analysis
- `author_influence_analysis`: Community influencer metrics
- `video_context_analysis`: YouTube video discussion analysis

### **Performance Optimizations**
- **Streamlit Caching**: TTL-based data caching for performance
- **Modular Architecture**: Separated concerns for maintainability
- **Lazy Loading**: On-demand data loading for heavy operations
- **Error Handling**: Graceful degradation with fallback displays

## 📊 Data Quality Improvements

### **Artist Name Normalization**
- **Duplicate Resolution**: BABYMETAL/Babymetal/BabyMetal → BABYMETAL
- **20+ Artist Mappings**: Standardized popular Japanese artist names
- **Consistent Casing**: Proper formatting across all visualizations

### **Genre Standardization**
- **50+ Genre Mappings**: Normalized genre variations (J-Pop/jpop/j-pop → J-Pop)
- **Hierarchical Grouping**: Metal subgenres, electronic variations
- **Cross-platform Consistency**: Unified genre names across data sources

## 🎨 UI/UX Features

### **Standardized Components**
- **Page Headers**: Consistent styling with descriptions and icons
- **Metric Cards**: Standardized KPI displays
- **Interactive Charts**: Plotly-based visualizations with hover data
- **Export Functions**: CSV/JSON download capabilities
- **Search & Filter**: Real-time filtering across all major sections

### **Responsive Design**
- **Mobile-Friendly**: Responsive layouts for different screen sizes
- **Tab Organization**: Logical grouping of related features
- **Intuitive Navigation**: Clear section separation and breadcrumbs

## 🔧 Recent Enhancements

### **Genre Analysis Improvements**
- ✅ Removed quick selection buttons for cleaner interface
- ✅ Enhanced artist discovery with search and ranking
- ✅ Complete artist export functionality (CSV/JSON)
- ✅ Artist name deduplication and normalization

### **Architecture Consolidation**
- ✅ Reduced from 11 fragmented pages to 6 focused sections
- ✅ Centralized data management with consistent caching
- ✅ Standardized UI library with reusable components
- ✅ Modular page structure for better maintainability

### **AI Integration**
- ✅ Comprehensive AI Intelligence Center with 4 analysis modes
- ✅ Smart search across all AI-generated insights
- ✅ Trend prediction and pattern recognition
- ✅ Sentiment health scoring and analysis

## 📈 Future Roadmap

- **Real-time Data Streaming**: Live updates from social media APIs
- **Advanced ML Models**: Custom recommendation and prediction models
- **User Personalization**: Customizable dashboards and saved searches
- **API Endpoints**: RESTful API for external data access
- **Advanced Export**: PDF reports and scheduled exports

---

**🎌 Japanese Music Trends Dashboard** | Powered by DBT, Streamlit & AI Analytics
- **Expandable Insights**: Organized by artist with collapsible sections
- **Session State Management**: Persistent search terms across page interactions

## 🚀 Usage

### Local Development
```bash
cd dashboard
streamlit run main_dashboard.py
```

### Docker
```bash
docker-compose up streamlit_dashboard
```

## 📋 Module Details

### `main_dashboard.py`
- Main application entry point
- Orchestrates all components
- Handles data loading and routing to pages
- Replaces the monolithic `dashboard_dbt.py`

### `database_service.py`
- Database connection management
- Core data fetching functionality
- SQLAlchemy engine caching

### `data_queries.py`
- All DBT model query functions
- Data transformation utilities (URL decoding, etc.)
- Cached data retrieval functions

### `visualizations.py`
- Chart creation functions (Plotly, Matplotlib)
- Word cloud generation
- Reusable visualization components

### `ui_components.py`
- Streamlit styling and CSS
- Reusable UI components (metrics, cards, etc.)
- Layout helpers and formatting functions

### `dashboard_pages.py`
- Individual page implementations
- Page-specific logic and layouts
- Navigation between different dashboard sections

## 🔧 Configuration

The dashboard uses environment variables for database connection:
- `WAREHOUSE_USER`
- `WAREHOUSE_PASSWORD`
- `WAREHOUSE_HOST`
- `WAREHOUSE_PORT`
- `WAREHOUSE_DB`

## 📊 Dashboard Pages

1. **🏠 Overview** - Key metrics and trending artists
2. **🎤 Artist Trends** - Detailed artist analysis
3. **🎶 Genre Analysis** - Genre performance and diversity
4. **☁️ Word Cloud** - Most discussed terms
5. **📱 Platform Insights** - Platform comparison
6. **💭 Sentiment Deep Dive** - Sentiment analysis
7. **📈 AI Trend Summary** - AI-generated trends
8. **🔍 AI Insights** - AI-generated insights

## 🎯 Future Improvements

- Add unit tests for each module
- Implement error logging
- Add configuration management
- Create API endpoints for data access
- Add caching strategies for better performance

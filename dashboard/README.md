# Japanese Music Trends Dashboard

A modular Streamlit dashboard for analyzing Japanese music trends from social media data using DBT models.

## ✅ Status: Fully Refactored & Restored

**Refactoring Complete**: Successfully converted from a 1325+ line monolithic file (`dashboard_dbt.py`) into a clean, modular architecture with full feature parity including all original AI-powered visualizations and interactive functionality.

## 🏗️ Architecture

The dashboard is now organized into separate modules for better maintainability:

### Module Structure

```
dashboard/
├── __init__.py              # Package initialization
├── main_dashboard.py        # Main entry point (replaces dashboard_dbt.py)
├── database_service.py      # Database connections and data fetching
├── data_queries.py          # DBT model query functions
├── visualizations.py        # Chart creation and plotting functions
├── ui_components.py         # Streamlit UI components and styling
├── dashboard_pages.py       # Individual page logic
├── config.py                # Configuration (existing)
├── Dockerfile               # Docker configuration
└── pyproject.toml           # Dependencies
```

### Key Benefits

1. **Modularity**: Each module has a single responsibility
2. **Maintainability**: Easier to find and modify specific functionality
3. **Testability**: Individual modules can be tested in isolation
4. **Reusability**: Components can be reused across different pages
5. **Readability**: Reduced file sizes and clearer code organization

## 🧠 Restored AI Features

### AI Trend Summary Page
- **Interactive Charts**: Genre popularity pie charts, sentiment bar charts, engagement distribution
- **Artist Visualization**: Horizontal bar chart showing trend strength vs sentiment with hover data
- **Rich Metrics**: Analysis date, total artists, trend counts with proper formatting
- **Data Tables**: Detailed artist metrics with all original columns

### AI Insights Page  
- **Advanced Search**: Real-time search across artist names and insight text
- **Multiple View Modes**: Search Results, Browse All, Summary Only
- **Interactive Filtering**: Regex-safe search with proper error handling
- **Search Highlighting**: Bold highlighting of search terms in results
- **Word Cloud Generation**: Dynamic word clouds from filtered insights
- **Quick Artist Navigation**: Button-based artist selection for easy browsing
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

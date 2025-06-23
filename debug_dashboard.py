"""
Debug Dashboard - Simple version to test database connectivity and data
"""

import streamlit as st
import pandas as pd
import traceback
import sys
import os

# Add the dashboard_online directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard_online'))

from data_manager import DataManager

# Configure Streamlit page
st.set_page_config(
    page_title="🔍 Debug Dashboard",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Debug Dashboard")
st.write("This page helps debug database connectivity and data loading issues.")

# Test database connection
st.header("1. Database Connection Test")
try:
    # Test basic connection
    from database_service import DatabaseService
    db_service = DatabaseService()
    st.success("✅ Database service initialized successfully")
    
    # Test simple query
    test_query = "SELECT current_database(), current_user;"
    result = db_service.fetch_data(test_query)
    if not result.empty:
        st.success("✅ Database connection working")
        st.write("Connection info:", result)
    else:
        st.error("❌ Database connection failed - no result")
        
except Exception as e:
    st.error(f"❌ Database connection failed: {str(e)}")
    st.code(traceback.format_exc())

# Test schema existence
st.header("2. Schema Test")
try:
    schema_query = """
    SELECT schema_name 
    FROM information_schema.schemata 
    WHERE schema_name IN ('analytics', 'intermediate')
    ORDER BY schema_name;
    """
    
    from database_service import DatabaseService
    db_service = DatabaseService()
    schemas = db_service.fetch_data(schema_query)
    
    if not schemas.empty:
        st.success(f"✅ Found schemas: {schemas['schema_name'].tolist()}")
    else:
        st.error("❌ Analytics/intermediate schemas not found")
        
except Exception as e:
    st.error(f"❌ Schema check failed: {str(e)}")

# Test table existence
st.header("3. Table Existence Test")
try:
    table_query = """
    SELECT table_schema, table_name, table_type
    FROM information_schema.tables 
    WHERE table_schema IN ('analytics', 'intermediate')
    ORDER BY table_schema, table_name;
    """
    
    tables = db_service.fetch_data(table_query)
    
    if not tables.empty:
        st.success(f"✅ Found {len(tables)} tables/views")
        st.dataframe(tables)
    else:
        st.error("❌ No tables/views found in analytics/intermediate schemas")
        
except Exception as e:
    st.error(f"❌ Table check failed: {str(e)}")

# Test data counts
st.header("4. Data Count Test")
try:
    count_queries = {
        "entity_extraction": "SELECT COUNT(*) as count FROM analytics.entity_extraction",
        "sentiment_analysis": "SELECT COUNT(*) as count FROM analytics.sentiment_analysis", 
        "int_extracted_artists": "SELECT COUNT(*) as count FROM analytics.int_extracted_artists",
        "artist_trends": "SELECT COUNT(*) as count FROM analytics.artist_trends",
        "genre_trends": "SELECT COUNT(*) as count FROM analytics.genre_trends"
    }
    
    for table_name, query in count_queries.items():
        try:
            result = db_service.fetch_data(query)
            count = result.iloc[0]['count'] if not result.empty else 0
            if count > 0:
                st.success(f"✅ {table_name}: {count:,} rows")
            else:
                st.warning(f"⚠️ {table_name}: {count} rows (empty)")
        except Exception as e:
            st.error(f"❌ {table_name}: Error - {str(e)}")
            
except Exception as e:
    st.error(f"❌ Data count check failed: {str(e)}")

# Test DataManager functions
st.header("5. DataManager Test")
try:
    st.write("Testing DataManager.get_overall_stats()...")
    stats = DataManager.get_overall_stats()
    st.write("Stats result:", stats)
    
    if stats:
        st.success("✅ DataManager.get_overall_stats() working")
    else:
        st.warning("⚠️ DataManager.get_overall_stats() returned empty/None")
        
except Exception as e:
    st.error(f"❌ DataManager test failed: {str(e)}")
    st.code(traceback.format_exc())

# Test artist data
try:
    st.write("Testing DataManager.get_artist_trends()...")
    artist_data = DataManager.get_artist_trends()
    st.write("Artist data shape:", artist_data.shape if hasattr(artist_data, 'shape') else "Not a DataFrame")
    
    if not artist_data.empty:
        st.success(f"✅ DataManager.get_artist_trends() working - {len(artist_data)} artists")
        st.dataframe(artist_data.head())
    else:
        st.warning("⚠️ DataManager.get_artist_trends() returned empty DataFrame")
        
except Exception as e:
    st.error(f"❌ Artist data test failed: {str(e)}")
    st.code(traceback.format_exc())

st.header("6. Raw Query Test")
try:
    st.write("Testing direct view query...")
    view_query = "SELECT * FROM analytics.overall_stats_dashboard LIMIT 1;"
    result = db_service.fetch_data(view_query)
    
    if not result.empty:
        st.success("✅ overall_stats_dashboard view working")
        st.write("Result:", result.to_dict('records'))
    else:
        st.warning("⚠️ overall_stats_dashboard view returned no data")
        
except Exception as e:
    st.error(f"❌ View query failed: {str(e)}")
    st.code(traceback.format_exc())

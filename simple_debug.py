#!/usr/bin/env python3
"""
Simple Streamlit App with Direct Secrets Access
This bypasses the complex configuration system.
"""

import streamlit as st
import sys
import os

# Add dashboard_online to path
dashboard_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dashboard_online')
sys.path.insert(0, dashboard_dir)
os.chdir(dashboard_dir)

st.title("🔧 Simple Database Connection Test")

# Direct secrets access
st.subheader("Secrets Check")

if hasattr(st, 'secrets'):
    st.success("✅ st.secrets is available")
    
    if st.secrets:
        st.write("**Available sections:**")
        for key in st.secrets.keys():
            st.write(f"- {key}")
            
        if 'database' in st.secrets:
            st.success("✅ Found database section")
            
            # Show configuration (without password)
            st.write("**Database configuration:**")
            st.write(f"- Host: {st.secrets.database.host}")
            st.write(f"- Port: {st.secrets.database.port}")
            st.write(f"- Database: {st.secrets.database.database}")
            st.write(f"- Username: {st.secrets.database.username}")
            st.write(f"- Password: {'*' * len(str(st.secrets.database.password))}")
            
            # Test connection
            if st.button("Test Database Connection"):
                try:
                    from sqlalchemy import create_engine, text
                    
                    # Direct connection string
                    connection_string = f"postgresql+psycopg2://{st.secrets.database.username}:{st.secrets.database.password}@{st.secrets.database.host}:{st.secrets.database.port}/{st.secrets.database.database}?sslmode=require"
                    
                    engine = create_engine(connection_string)
                    
                    with engine.connect() as conn:
                        result = conn.execute(text("SELECT version()"))
                        version = result.fetchone()[0]
                        st.success("✅ Database connection successful!")
                        st.info(f"PostgreSQL: {version[:50]}...")
                        
                        # Check for analytics schema
                        schemas_result = conn.execute(text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'analytics'"))
                        analytics_exists = schemas_result.fetchone()
                        
                        if analytics_exists:
                            st.success("✅ Analytics schema found")
                            
                            # Check for key tables
                            tables_result = conn.execute(text("""
                                SELECT table_name FROM information_schema.tables 
                                WHERE table_schema = 'analytics' 
                                AND table_name IN ('trend_summary_overview', 'artist_trends', 'genre_trends')
                            """))
                            tables = [row[0] for row in tables_result.fetchall()]
                            
                            if tables:
                                st.success(f"✅ Found tables: {', '.join(tables)}")
                                st.success("🎉 Your database is ready! You can now use the main dashboard.")
                            else:
                                st.warning("⚠️ Analytics tables not found. You need to migrate your data.")
                                
                        else:
                            st.warning("⚠️ Analytics schema not found. You need to migrate your data.")
                            
                except Exception as e:
                    st.error(f"❌ Connection failed: {str(e)}")
                    
                    if "password authentication failed" in str(e).lower():
                        st.error("The username or password is incorrect.")
                    elif "does not exist" in str(e).lower():
                        st.error("The database or host does not exist.")
                    elif "ssl" in str(e).lower():
                        st.error("SSL connection issue. Supabase requires SSL.")
        else:
            st.error("❌ No 'database' section found in secrets")
            st.write("Your secrets should have a `[database]` section.")
    else:
        st.error("❌ st.secrets exists but is empty")
else:
    st.error("❌ st.secrets not available")

st.subheader("Next Steps")

if hasattr(st, 'secrets') and 'database' in st.secrets:
    st.success("Your secrets look good! If the connection test works, you can switch back to the main dashboard.")
else:
    st.error("Please fix your secrets configuration:")
    st.code("""
[database]
host = "db.swjvbxebxxfrrmmkdnyg.supabase.co"
port = 5432
database = "postgres"
username = "postgres"
password = "nYwH9g8I2J3ETrKS"
    """)

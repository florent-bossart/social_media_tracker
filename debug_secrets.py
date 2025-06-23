#!/usr/bin/env python3
"""
Streamlit Secrets Debugging Tool
This file helps debug Streamlit Cloud secrets configuration.
"""

import streamlit as st
import os

st.title("🔧 Streamlit Secrets Debug Tool")

st.write("This tool helps you debug your Streamlit Cloud secrets configuration.")

# Check Streamlit secrets
st.subheader("1. Streamlit Secrets Check")

if hasattr(st, 'secrets'):
    st.success("✅ st.secrets is available")
    
    if st.secrets:
        st.write("**Available secret sections:**")
        for key in st.secrets.keys():
            st.write(f"- `{key}`")
        
        if 'database' in st.secrets:
            st.success("✅ Found 'database' section in secrets")
            
            st.write("**Database configuration:**")
            try:
                db_secrets = st.secrets.database
                st.write(f"- Host: `{db_secrets.host}`")
                st.write(f"- Port: `{db_secrets.port}`")
                st.write(f"- Database: `{db_secrets.database}`")
                st.write(f"- Username: `{db_secrets.username}`")
                st.write(f"- Password: `{'*' * len(str(db_secrets.password))}`")
                
                # Test connection
                st.subheader("2. Database Connection Test")
                if st.button("Test Database Connection"):
                    try:
                        from sqlalchemy import create_engine, text
                        
                        connection_string = f"postgresql://{db_secrets.username}:{db_secrets.password}@{db_secrets.host}:{db_secrets.port}/{db_secrets.database}"
                        engine = create_engine(connection_string)
                        
                        with engine.connect() as conn:
                            result = conn.execute(text("SELECT version()"))
                            version = result.fetchone()[0]
                            st.success(f"✅ Database connection successful!")
                            st.info(f"PostgreSQL version: {version}")
                            
                            # Check for schemas
                            schemas_result = conn.execute(text("SELECT schema_name FROM information_schema.schemata WHERE schema_name IN ('analytics', 'raw', 'intermediate')"))
                            schemas = [row[0] for row in schemas_result.fetchall()]
                            
                            if schemas:
                                st.success(f"✅ Found schemas: {', '.join(schemas)}")
                            else:
                                st.warning("⚠️ No analytics schemas found. You may need to import your data.")
                                
                    except Exception as e:
                        st.error(f"❌ Database connection failed: {str(e)}")
                        
            except Exception as e:
                st.error(f"❌ Error reading database secrets: {str(e)}")
                
        else:
            st.error("❌ No 'database' section found in secrets")
            st.write("**Your secrets should look like this:**")
            st.code("""
[database]
host = "db.swjvbxebxxfrrmmkdnyg.supabase.co"
port = 5432
database = "postgres"
username = "postgres"
password = "nYwH9g8I2J3ETrKS"
            """)
    else:
        st.error("❌ st.secrets exists but is empty")
else:
    st.error("❌ st.secrets is not available")

# Check environment variables
st.subheader("3. Environment Variables Check")

env_vars = ['ONLINE_DB_HOST', 'ONLINE_DB_PASSWORD', 'ONLINE_DB_NAME', 'ONLINE_DB_USER', 'ONLINE_DB_PORT']
found_env_vars = []

for var in env_vars:
    value = os.getenv(var)
    if value:
        found_env_vars.append(var)
        if 'PASSWORD' in var:
            st.write(f"- `{var}`: `{'*' * len(value)}`")
        else:
            st.write(f"- `{var}`: `{value}`")

if found_env_vars:
    st.info(f"Found {len(found_env_vars)} environment variables")
else:
    st.info("No environment variables found (this is normal for Streamlit Cloud)")

# Instructions
st.subheader("4. Next Steps")

if hasattr(st, 'secrets') and 'database' in st.secrets:
    st.success("🎉 Your secrets are configured correctly! You can now use your main dashboard.")
else:
    st.error("❌ Secrets not configured properly. Please:")
    st.write("1. Go to your Streamlit Cloud app settings")
    st.write("2. Click on 'Secrets' tab")
    st.write("3. Add the database configuration in TOML format")
    st.write("4. Wait 1 minute for changes to propagate")
    st.write("5. Refresh this page")

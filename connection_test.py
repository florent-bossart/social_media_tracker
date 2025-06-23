#!/usr/bin/env python3
"""
Supabase Connection Test
Simple test to verify Supabase database connectivity.
"""

import streamlit as st
import psycopg2
from sqlalchemy import create_engine, text

st.title("🔍 Supabase Connection Diagnostics")

if hasattr(st, 'secrets') and 'database' in st.secrets:
    st.success("✅ Secrets configured properly")
    
    # Show connection details (without password)
    st.subheader("Connection Details")
    st.write(f"**Host:** {st.secrets.database.host}")
    st.write(f"**Port:** {st.secrets.database.port}")
    st.write(f"**Database:** {st.secrets.database.database}")
    st.write(f"**Username:** {st.secrets.database.username}")
    
    if st.button("Test Connection Methods"):
        
        # Method 1: Basic psycopg2
        st.subheader("Method 1: Direct psycopg2")
        try:
            conn = psycopg2.connect(
                host=st.secrets.database.host,
                port=st.secrets.database.port,
                database=st.secrets.database.database,
                user=st.secrets.database.username,
                password=st.secrets.database.password,
                sslmode='require',
                connect_timeout=10
            )
            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            conn.close()
            st.success(f"✅ Direct psycopg2 connection successful!")
            st.info(f"PostgreSQL: {version[:50]}...")
        except Exception as e:
            st.error(f"❌ Direct psycopg2 failed: {e}")
        
        # Method 2: SQLAlchemy with SSL required
        st.subheader("Method 2: SQLAlchemy with SSL")
        try:
            connection_string = f"postgresql+psycopg2://{st.secrets.database.username}:{st.secrets.database.password}@{st.secrets.database.host}:{st.secrets.database.port}/{st.secrets.database.database}?sslmode=require"
            engine = create_engine(connection_string, connect_args={"connect_timeout": 10})
            with engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
            st.success(f"✅ SQLAlchemy SSL connection successful!")
            st.info(f"PostgreSQL: {version[:50]}...")
        except Exception as e:
            st.error(f"❌ SQLAlchemy SSL failed: {e}")
        
        # Method 3: SQLAlchemy with SSL preferred
        st.subheader("Method 3: SQLAlchemy with SSL preferred")
        try:
            connection_string = f"postgresql+psycopg2://{st.secrets.database.username}:{st.secrets.database.password}@{st.secrets.database.host}:{st.secrets.database.port}/{st.secrets.database.database}?sslmode=prefer"
            engine = create_engine(connection_string, connect_args={"connect_timeout": 10})
            with engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
            st.success(f"✅ SQLAlchemy SSL preferred connection successful!")
            st.info(f"PostgreSQL: {version[:50]}...")
        except Exception as e:
            st.error(f"❌ SQLAlchemy SSL preferred failed: {e}")
        
        # Method 4: Check if database has tables
        st.subheader("Method 4: Database Content Check")
        try:
            # Use whichever method worked above
            connection_string = f"postgresql+psycopg2://{st.secrets.database.username}:{st.secrets.database.password}@{st.secrets.database.host}:{st.secrets.database.port}/{st.secrets.database.database}?sslmode=prefer"
            engine = create_engine(connection_string, connect_args={"connect_timeout": 10})
            
            with engine.connect() as conn:
                # Check for schemas
                schemas_result = conn.execute(text("""
                    SELECT schema_name FROM information_schema.schemata 
                    WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                """))
                schemas = [row[0] for row in schemas_result.fetchall()]
                
                if schemas:
                    st.success(f"✅ Found schemas: {', '.join(schemas)}")
                    
                    # Check for analytics tables
                    if 'analytics' in schemas:
                        tables_result = conn.execute(text("""
                            SELECT table_name FROM information_schema.tables 
                            WHERE table_schema = 'analytics'
                        """))
                        tables = [row[0] for row in tables_result.fetchall()]
                        
                        if tables:
                            st.success(f"✅ Found analytics tables: {', '.join(tables[:5])}{'...' if len(tables) > 5 else ''}")
                            st.info(f"Total analytics tables: {len(tables)}")
                        else:
                            st.warning("⚠️ Analytics schema exists but no tables found")
                    else:
                        st.warning("⚠️ No analytics schema found - you need to import your data")
                else:
                    st.warning("⚠️ No custom schemas found - database appears empty")
                    
        except Exception as e:
            st.error(f"❌ Database content check failed: {e}")
    
    # Additional diagnostics
    st.subheader("Network Diagnostics")
    st.info("The error 'Cannot assign requested address' often indicates:")
    st.write("1. **IPv6 connectivity issues** - Streamlit Cloud might not support IPv6")
    st.write("2. **Firewall restrictions** - Some cloud providers block certain connections")
    st.write("3. **SSL configuration** - Supabase requires proper SSL setup")
    st.write("4. **Connection pooling** - Too many concurrent connections")
    
    st.subheader("Recommended Solutions")
    st.write("1. **Check Supabase status** - Visit status.supabase.com")
    st.write("2. **Verify database is running** - Check your Supabase dashboard")
    st.write("3. **Review connection limits** - Supabase has connection limits")
    st.write("4. **Try different SSL modes** - Use the test above")

else:
    st.error("❌ Database secrets not configured")
    st.code("""
[database]
host = "db.swjvbxebxxfrrmmkdnyg.supabase.co"
port = 5432
database = "postgres"
username = "postgres"
password = "nYwH9g8I2J3ETrKS"
    """)

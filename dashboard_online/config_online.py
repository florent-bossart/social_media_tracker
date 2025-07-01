import os
import streamlit as st
from sqlalchemy import create_engine

def safe_get_env_int(key, default=None):
    """Safely get an environment variable and convert to int."""
    try:
        value = os.getenv(key, str(default) if default is not None else None)
        if value is None:
            return default
        # Extra defensive check - ensure value is converted to string
        value_str = str(value)
        if value_str.lower() == 'none' or value_str.strip() == '':
            return default
        return int(value_str)
    except (ValueError, TypeError, AttributeError):
        return default

def safe_get_env_str(key, default=None):
    """Safely get an environment variable as string."""
    try:
        value = os.getenv(key, default)
        if value is None:
            return default
        # Extra defensive check
        value_str = str(value)
        if value_str.lower() == 'none':
            return default
        return value_str
    except (AttributeError, TypeError):
        return default

def get_database_config():
    """Get database configuration for online deployment."""

    # Debug information
    debug_info = []

    # Try Streamlit secrets first (for Streamlit Cloud deployment)
    try:
        debug_info.append(f"Checking Streamlit secrets...")
        debug_info.append(f"st.secrets exists: {hasattr(st, 'secrets')}")

        if hasattr(st, 'secrets'):
            debug_info.append(f"st.secrets keys: {list(st.secrets.keys()) if st.secrets else 'None'}")

            if 'database' in st.secrets:
                debug_info.append("Found database section in secrets")
                secrets_db = st.secrets['database']

                # Safely get port from secrets with extra defensive programming
                port_value = secrets_db.get('port', 5432)
                try:
                    if port_value is None:
                        port_value = 5432
                    elif isinstance(port_value, str):
                        if port_value.lower() == 'none' or port_value.strip() == '':
                            port_value = 5432
                        else:
                            port_value = int(port_value)
                    elif isinstance(port_value, (int, float)):
                        port_value = int(port_value)
                    else:
                        port_value = 5432
                except (ValueError, TypeError, AttributeError):
                    port_value = 5432

                db_config = {
                    'host': secrets_db.get('host'),
                    'port': port_value,
                    'database': secrets_db.get('database'),
                    'username': secrets_db.get('username', 'postgres.swjvbxebxxfrrmmkdnyg'),
                    'password': secrets_db.get('password')
                }
                debug_info.append(f"Database config from secrets: host={db_config['host'][:10] + '...' if db_config['host'] else 'None'}, port={db_config['port']}")
                if db_config['host'] and db_config['password']:
                    return db_config
                else:
                    debug_info.append("Missing required secrets (host or password)")
            else:
                debug_info.append("No 'database' section found in secrets")
        else:
            debug_info.append("st.secrets not available")

    except Exception as e:
        debug_info.append(f"Error reading Streamlit secrets: {str(e)}")

    # Fallback to environment variables (for local testing)
    debug_info.append("Trying environment variables...")
    online_db_host = safe_get_env_str("HOST")
    online_db_password = safe_get_env_str("PASSWORD")
    online_db_name = safe_get_env_str("DATABASE")
    online_db_user = safe_get_env_str("USERNAME", 'postgres.swjvbxebxxfrrmmkdnyg')
    online_db_port = safe_get_env_int("PORT", 5432)

    debug_info.append(f"Environment variables: host={online_db_host[:10] + '...' if online_db_host else 'None'}, password={'*' * len(online_db_password) if online_db_password else 'None'}, port={online_db_port}")

    if online_db_host and online_db_password:
        debug_info.append("Using environment variables")
        return {
            'host': online_db_host,
            'port': online_db_port,
            'database': online_db_name,
            'username': online_db_user,
            'password': online_db_password
        }

    # If no configuration found, provide detailed error
    error_msg = "No database configuration found. Debug info:\n" + "\n".join(debug_info)
    raise ValueError(error_msg)

def get_database_engine():
    """Create and return a database engine for the online deployment."""
    config = get_database_config()

    # Create the connection string
    connection_string = (
    f"postgresql+psycopg2://{config['username']}:{config['password']}"
    f"@{config['host']}:{config['port']}/{config['database']}?sslmode=require"
    )

    # Create the engine
    engine = create_engine(
        connection_string,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,    # Recycle connections after 5 minutes
        connect_args={
            "sslmode": "require",  # Supabase requires SSL
            "connect_timeout": 30
        }
    )

    return engine

def test_database_connection():
    """Test the database connection."""
    try:
        engine = get_database_engine()
        with engine.connect() as conn:
            result = conn.execute("SELECT 1 as test")
            return True, "Connection successful!"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"

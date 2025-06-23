# Streamlit Cloud Deployment Guide

## 🚀 Deploy Your Social Media Analytics Dashboard

### Prerequisites
- [x] Supabase account created
- [x] Database imported via SQL script
- [x] GitHub repository with this code

### Step 1: Deploy Database to Supabase

1. **Go to your Supabase Dashboard**
2. **Open SQL Editor** (left sidebar)
3. **Create new query**
4. **Copy the contents of `supabase_import/database_backup.sql`**
5. **Paste and run the SQL script**
6. **Verify tables were created** in Table Editor

### Step 2: Deploy to Streamlit Cloud

1. **Go to [share.streamlit.io](https://share.streamlit.io)**
2. **Sign in with GitHub**
3. **Click "New app"**
4. **Select your repository**: `florent-bossart/social_media_tracker`
5. **Set main file path**: `streamlit_app.py`
6. **Advanced settings**:
   - **Python version**: 3.9 or 3.10
   - **Requirements file**: `requirements.txt`

### Step 3: Configure Secrets

1. **In Streamlit Cloud app settings**, go to **"Secrets"**
2. **Add your database configuration** in TOML format:
   ```toml
   [database]
   host = "db.swjvbxebxxfrrmmkdnyg.supabase.co"
   port = 5432
   database = "postgres"
   username = "postgres"
   password = "nYwH9g8I2J3ETrKS"
   ```
3. **Click "Save"**
4. **Wait 1 minute** for changes to propagate

### Step 3.5: Debug Secrets (If Having Issues)

If you get "No database configuration found" errors:

1. **Temporarily change your main file** to `debug_secrets.py`
2. **Deploy and check** what the debug tool shows
3. **Fix any issues** with your secrets configuration
4. **Change main file back** to `streamlit_app.py`

### Step 4: Deploy and Test

1. **Click "Deploy"**
2. **Wait for deployment** (usually 2-5 minutes)
3. **Test the dashboard** functionality
4. **Share the public URL** with others!

## 📁 Files Created for Deployment

- `streamlit_app.py` - Entry point for Streamlit Cloud
- `requirements.txt` - Python dependencies
- `.streamlit/config.toml` - Streamlit configuration
- `.streamlit/secrets.toml` - Template for database credentials
- `dashboard_online/` - Online version of dashboard

## 🔧 Troubleshooting

### Common Issues:

1. **"No database configuration found" Error**
   - Use the debug tool: Change main file to `debug_secrets.py`
   - Check that secrets are in exact TOML format with `[database]` section
   - Verify credentials are correct (host should start with `db.` and end with `.supabase.co`)
   - Wait 1 minute after saving secrets for changes to propagate

2. **Database Connection Failed**
   - Verify Supabase credentials in your Supabase dashboard
   - Check that your Supabase project is active
   - Ensure database was imported/migrated correctly

3. **Module Import Errors**
   - Check requirements.txt has all dependencies
   - Verify Python version is 3.9 or 3.10

4. **Dashboard Not Loading**
   - Check Streamlit Cloud logs for detailed error messages
   - Verify streamlit_app.py path is correct

### Debug Steps:

1. **Test secrets configuration**:
   - Change main file to `debug_secrets.py`
   - Deploy and check what it shows
   - Fix any configuration issues
   - Change back to `streamlit_app.py`

2. **Check database content**:
   - Log into your Supabase dashboard
   - Go to Table Editor
   - Verify that analytics tables exist with data

### Testing Locally:

```bash
# Test the online dashboard locally
cd dashboard_online
streamlit run main_dashboard.py

# Or test the Streamlit Cloud entry point
streamlit run streamlit_app.py
```

## 🎉 Success!

Once deployed, your dashboard will be available at:
`https://your-app-name.streamlit.app`

The dashboard will show:
- **Japanese Music Analytics**: Artist trends, genre analysis
- **Social Media Insights**: YouTube/Reddit sentiment analysis
- **Temporal Trends**: Time-based analytics
- **Interactive Visualizations**: Charts, wordclouds, metrics

Perfect for showcasing your data science and social media analytics skills! 🚀

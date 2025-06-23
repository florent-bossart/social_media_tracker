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
2. **Copy the contents from `.streamlit/secrets.toml`**
3. **Paste into the secrets editor**
4. **Update with your actual Supabase credentials**:
   ```toml
   [database]
   host = "db.your-project.supabase.co"
   port = 5432
   database = "postgres"
   username = "postgres"
   password = "your-actual-password"
   ```

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

1. **Database Connection Failed**
   - Check secrets configuration
   - Verify Supabase credentials
   - Ensure database was imported correctly

2. **Module Import Errors**
   - Check requirements.txt has all dependencies
   - Verify Python version compatibility

3. **Dashboard Not Loading**
   - Check Streamlit Cloud logs
   - Verify streamlit_app.py path is correct

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

#!/bin/bash
"""
Direct database test using Docker exec
"""

echo "🔧 Testing database integration via Docker..."

# Check current record counts
echo "📊 Current database state:"
docker exec social_media_tracker-social_media_tracker_db-1 psql -U dbt -d social_db -c "
SELECT
    'entity_extraction' as table_name, COUNT(*) as records FROM analytics.entity_extraction
UNION ALL
SELECT
    'sentiment_analysis' as table_name, COUNT(*) as records FROM analytics.sentiment_analysis
UNION ALL
SELECT
    'trend_analysis' as table_name, COUNT(*) as records FROM analytics.trend_analysis
UNION ALL
SELECT
    'summarization_metrics' as table_name, COUNT(*) as records FROM analytics.summarization_metrics
UNION ALL
SELECT
    'summarization_insights' as table_name, COUNT(*) as records FROM analytics.summarization_insights
ORDER BY table_name;
"

echo -e "\n🧹 Clearing all pipeline data..."

# Clear all tables with RESTART IDENTITY
docker exec social_media_tracker-social_media_tracker_db-1 psql -U dbt -d social_db -c "
TRUNCATE TABLE analytics.entity_extraction RESTART IDENTITY CASCADE;
TRUNCATE TABLE analytics.sentiment_analysis RESTART IDENTITY CASCADE;
TRUNCATE TABLE analytics.trend_analysis RESTART IDENTITY CASCADE;
TRUNCATE TABLE analytics.summarization_metrics RESTART IDENTITY CASCADE;
TRUNCATE TABLE analytics.summarization_insights RESTART IDENTITY CASCADE;
"

echo "✅ Data cleared successfully"

# Verify tables are empty
echo -e "\n📊 Verifying tables are empty:"
docker exec social_media_tracker-social_media_tracker_db-1 psql -U dbt -d social_db -c "
SELECT
    'entity_extraction' as table_name, COUNT(*) as records FROM analytics.entity_extraction
UNION ALL
SELECT
    'sentiment_analysis' as table_name, COUNT(*) as records FROM analytics.sentiment_analysis
UNION ALL
SELECT
    'trend_analysis' as table_name, COUNT(*) as records FROM analytics.trend_analysis
UNION ALL
SELECT
    'summarization_metrics' as table_name, COUNT(*) as records FROM analytics.summarization_metrics
UNION ALL
SELECT
    'summarization_insights' as table_name, COUNT(*) as records FROM analytics.summarization_insights
ORDER BY table_name;
"

echo -e "\n✅ Database clearing test completed"

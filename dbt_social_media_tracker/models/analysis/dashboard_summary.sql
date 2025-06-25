-- Dashboard Summary
-- High-level dashboard summary for analytics
{{ config(materialized='view') }}

SELECT 
    'dashboard_summary' as summary_type,
    COUNT(DISTINCT artist_name) as total_artists,
    COUNT(*) as total_mentions,
    AVG(avg_sentiment_score) as overall_avg_sentiment,
    CURRENT_TIMESTAMP as last_updated
FROM {{ ref('artist_sentiment_dashboard') }}

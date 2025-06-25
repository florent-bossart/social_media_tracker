-- Daily Trends Dashboard
-- Basic daily trends view for analytics
{{ config(materialized='view') }}

SELECT
    'daily_trends' as dashboard_type,
    CURRENT_DATE as trend_date,
    COUNT(*) as total_mentions,
    'placeholder' as status
FROM {{ ref('artist_sentiment_dashboard') }}
GROUP BY trend_date

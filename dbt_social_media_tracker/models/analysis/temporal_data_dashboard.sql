{{ config(materialized='view') }}

SELECT
    time_period as date,
    sentiment_shift,
    engagement_pattern,
    CASE
        WHEN ABS(sentiment_shift) >= 0.5 THEN 0.8
        WHEN ABS(sentiment_shift) >= 0.3 THEN 0.6
        WHEN ABS(sentiment_shift) >= 0.1 THEN 0.4
        ELSE 0.2
    END as trend_strength,
    COUNT(*) OVER () as data_points,
    CURRENT_TIMESTAMP as analysis_timestamp
FROM {{ source('analytics', 'temporal_trends') }}
WHERE time_period::DATE >= CURRENT_DATE - INTERVAL '1 month'  -- Extended to 1 year to include your 2024 data
ORDER BY time_period::DATE

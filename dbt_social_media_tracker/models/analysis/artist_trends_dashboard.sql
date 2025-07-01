{{ config(materialized='view') }}

WITH artist_stats AS (
    SELECT
        artist_name_lower,
        artist_name,
        COUNT(*) as mention_count,
        AVG(confidence_score) as avg_confidence,
        COUNT(DISTINCT source_platform) as platform_count,
        AVG(COALESCE(sentiment_strength, 5.0)) as sentiment_score
    FROM {{ ref('int_extracted_artists') }}
    GROUP BY artist_name_lower, artist_name
    HAVING COUNT(*) >= 3  -- Only artists with at least 3 mentions
),
filtered_artists AS (
    SELECT
        artist_name_lower,
        artist_name,
        mention_count,
        avg_confidence,
        platform_count,
        sentiment_score
    FROM artist_stats
    WHERE artist_name_lower NOT IN ( 'moa', 'momo', 'su-metal', 'unknown')  -- Excluded from trending
        AND artist_name_lower NOT ILIKE 'hall of%'
        AND artist_name_lower NOT ILIKE '%playlist%'
        AND LENGTH(artist_name_lower) > 2
)
SELECT
    artist_name,
    CASE
        WHEN artist_name_lower = 'babymetal' THEN CAST(mention_count * 0.2 AS INTEGER)
        ELSE mention_count
    END as mention_count,
    sentiment_score,
    avg_confidence as trend_strength,
    CASE
        WHEN sentiment_score >= 7 THEN 'positive'
        WHEN sentiment_score <= 4 THEN 'negative'
        ELSE 'neutral'
    END as trend_direction,
    CASE
        WHEN mention_count >= 50 THEN 'high'
        WHEN mention_count >= 20 THEN 'medium'
        ELSE 'low'
    END as engagement_level,
    platform_count
FROM filtered_artists
ORDER BY mention_count DESC
